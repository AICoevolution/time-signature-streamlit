import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
from urllib.parse import urljoin, unquote
import sys

class KernExtractor:
    """
    Class to extract time signatures from Kern Humdrum database using the actual HTML structure
    """
    
    def __init__(self, base_url="https://kern.humdrum.org"):
        """Initialize with base URL and create necessary directories"""
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        os.makedirs("output", exist_ok=True)
        
        # List of available composers in Kern
        self.available_composers = [
            "Adam", "Alkan", "Bach", "Banchieri", "Beethoven", "Billings", "Bossi", 
            "Brahms", "Buxtehude", "Byrd", "Chopin", "Clementi", "Corelli", "Dufay", 
            "Dunstable", "Field", "Flecha", "Foster", "Frescobaldi", "Gershwin", 
            "Giovannelli", "Grieg", "Haydn", "Himmel", "Hummel", "Isaac", "Ives", 
            "Joplin", "Josquin", "Landini", "Lassus", "Liszt", "MacDowell", 
            "Mendelssohn", "Monteverdi", "Mozart", "Pachelbel", "Prokofiev", "Ravel", 
            "Scarlatti", "Schubert", "Schumann", "Scriabin", "Sinding", "Sousa", 
            "Turpin", "Vecchi", "Victoria", "Vivaldi", "Weber"
        ]
    
    def search_composer(self, composer, result_type="Text"):
        """
        Search for works by a composer and return the search results HTML
        
        Args:
            composer (str): Name of the composer to search for
            result_type (str): Type of results (Text, Instrumental, etc.)
            
        Returns:
            BeautifulSoup object of the search results page or None if failed
        """
        search_url = f"{self.base_url}/search?s=t&keyword={composer}&type={result_type}"
        print(f"Searching for {composer} at: {search_url}")
        
        try:
            response = requests.get(search_url, headers=self.headers)
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}")
                return None
            
            # Save the HTML for debugging if needed
            with open(f"output/{composer.lower().replace(' ', '_')}_search.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            return BeautifulSoup(response.text, 'html.parser')
        
        except Exception as e:
            print(f"Error searching: {e}")
            return None
    
    def extract_links_from_search(self, soup):
        """
        Extract links from the search results page using the exact HTML structure
        
        Args:
            soup (BeautifulSoup): Parsed HTML of the search results page
            
        Returns:
            list: List of dictionaries with work information and links
        """
        if not soup:
            return []
        
        works = []
        
        # Find all table rows (each row represents a work)
        rows = soup.find_all('tr')
        print(f"Found {len(rows)} rows in the search results")
        
        for row in rows:
            # Each work should have img elements with specific alt text or src attributes
            s_link = None
            h_link = None
            m_link = None
            k_link = None
            v_link = None
            
            # Find all images in this row
            img_elements = row.find_all('img')
            for img in img_elements:
                alt_text = img.get('alt', '')
                img_src = img.get('src', '')
                
                # Find the parent <a> tag that contains the actual link
                parent_link = img.parent
                if parent_link and parent_link.name == 'a':
                    href = parent_link.get('href', '')
                    
                    if alt_text == 'PDF Score' or 'button-S.gif' in img_src:
                        s_link = urljoin(self.base_url, href)
                    elif alt_text == 'Humdrum File' or 'button-H.gif' in img_src:
                        h_link = urljoin(self.base_url, href)
                    elif alt_text == 'MIDI File' or 'button-M.gif' in img_src:
                        m_link = urljoin(self.base_url, href)
                    elif alt_text == 'Keyscape' or 'button-K.gif' in img_src:
                        k_link = urljoin(self.base_url, href)
                    elif alt_text == 'Verovio Humdrum Viewer' or 'button-V.gif' in img_src:
                        v_link = urljoin(self.base_url, href)
            
            # Get the work title - it's often in the last link of the row
            title = None
            info_link = None
            
            # Look for links containing "format=info" which are usually work titles
            info_links = row.find_all('a', href=lambda href: href and 'format=info' in href)
            if info_links:
                info_link = info_links[-1]  # Use the last one if multiple exist
                title = info_link.text.strip()
                info_url = urljoin(self.base_url, info_link.get('href', ''))
            
            # If no title found, try to get any text from the row
            if not title:
                text_content = row.get_text().strip()
                if text_content:
                    # Try to extract a meaningful title from the text content
                    title = re.sub(r'\s+', ' ', text_content)
            
            # Only add works that have both a title and Humdrum (H) link
            if title and h_link:
                work_info = {
                    'title': title,
                    'links': {
                        'H': h_link
                    }
                }
                
                # Add other links if they exist
                if s_link:
                    work_info['links']['S'] = s_link
                if m_link:
                    work_info['links']['M'] = m_link
                if k_link:
                    work_info['links']['K'] = k_link
                if v_link:
                    work_info['links']['V'] = v_link
                if info_link:
                    work_info['links']['info'] = info_url
                
                works.append(work_info)
        
        print(f"Extracted {len(works)} works with H links")
        return works
    
    def extract_time_signature(self, h_link, s_link=None):
        """
        Extract time signature and metadata from a Humdrum file
        
        Args:
            h_link (str): URL to the Humdrum file (H link)
            s_link (str, optional): URL to the PDF score (S link)
            
        Returns:
            dict: Dictionary with time signature and metadata
        """
        result = {
            'time_signature': None,
            'title': None,
            'composer': None,
            'catalog_number': None,
            'reference_records': {},
            'pdf_link': s_link  # Store PDF link directly in metadata
        }
        
        try:
            print(f"Accessing: {h_link}")
            
            # Handle different URL formats
            if '&format=kern' in h_link:
                # Direct kern format
                response = requests.get(h_link, headers=self.headers)
                content_type = 'text/plain'
            else:
                # JSON format
                response = requests.get(h_link, headers=self.headers)
                content_type = response.headers.get('Content-Type', '')
            
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}")
                return result
            
            # Process response based on content type
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    
                    if isinstance(data, dict) and 'data' in data:
                        content = data['data']
                    else:
                        content = str(data)
                except:
                    content = response.text
            else:
                content = response.text
            
            # Save raw content for debugging (only if debugging flag is set)
            if os.environ.get("KERN_DEBUG", "0") == "1":
                filename = f"output/humdrum_sample_{int(time.time())}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content[:10000])  # Save first 10000 characters
            
            # Extract time signature - look for *M pattern
            time_sig_match = re.search(r'\*M(\d+)/(\d+)', content)
            if time_sig_match:
                result['time_signature'] = f"{time_sig_match.group(1)}/{time_sig_match.group(2)}"
            else:
                # Try mensural notation format
                met_match = re.search(r'\*met\(([^)]+)\)', content)
                if met_match:
                    result['time_signature'] = met_match.group(1)
            
            # Extract metadata from reference records (lines starting with !!!)
            ref_records = re.findall(r'!!!([^:]+):\s*(.+)', content)
            for key, value in ref_records:
                result['reference_records'][key] = value.strip()
                
                # Extract specific metadata
                if key == 'OTL':  # Original Title
                    result['title'] = value.strip()
                elif key == 'COM':  # Composer
                    result['composer'] = value.strip()
                elif key in ['SCT', 'ONB', 'OPC']:  # Catalog numbers
                    result['catalog_number'] = value.strip()
            
            return result
        
        except Exception as e:
            print(f"Error extracting time signature: {e}")
            return result
    
    def process_composer(self, composer, max_works=None):
        """
        Process works by a composer and extract time signatures
        
        Args:
            composer (str): Name of the composer
            max_works (int, optional): Maximum number of works to process
            
        Returns:
            dict: Dictionary of works with their time signatures
        """
        # Search for the composer
        soup = self.search_composer(composer)
        if not soup:
            return {}
        
        # Extract links
        works = self.extract_links_from_search(soup)
        
        # Limit works if specified
        if max_works and max_works < len(works):
            works = works[:max_works]
            print(f"Processing {max_works} out of {len(works)} works")
        
        composer_data = {}
        
        # Process each work
        for i, work in enumerate(works):
            print(f"\nProcessing work {i+1}/{len(works)}: {work['title']}")
            
            # Extract time signature
            if 'H' in work['links']:
                # Get the PDF link if available
                s_link = work['links'].get('S', None)
                
                metadata = self.extract_time_signature(work['links']['H'], s_link)
                
                if metadata['time_signature']:
                    print(f"  Found time signature: {metadata['time_signature']}")
                    
                    # Determine the work title
                    work_title = metadata['title'] if metadata['title'] else work['title']
                    
                    # Add catalog number if available
                    if metadata['catalog_number'] and metadata['catalog_number'] not in work_title:
                        work_title = f"{work_title} {metadata['catalog_number']}"
                    
                    # Create movement entry
                    if work_title not in composer_data:
                        composer_data[work_title] = []
                    
                    # Determine movement title (use work title if no specific movement title)
                    movement_title = work['title']
                    
                    # Add the movement with PDF link
                    movement_data = {
                        "movement": movement_title,
                        "time_signature": metadata['time_signature'],
                    }
                    
                    # Only add PDF link if it exists
                    if metadata['pdf_link']:
                        movement_data["pdf_link"] = metadata['pdf_link']
                    
                    # Check if this movement already exists
                    exists = False
                    for existing in composer_data[work_title]:
                        if existing['movement'] == movement_title or existing['time_signature'] == metadata['time_signature']:
                            exists = True
                            break
                    
                    if not exists:
                        composer_data[work_title].append(movement_data)
                    
                    # If PDF link is available, log it
                    if s_link:
                        print(f"  PDF Score available: {s_link}")
                
                else:
                    print("  No time signature found")
            
            # Delay to avoid overloading the server
            time.sleep(1)
        
        return composer_data
    
    def save_composer_data(self, composer, composer_data):
        """
        Save composer data to a JSON file
        
        Args:
            composer (str): Composer name
            composer_data (dict): Dictionary of works with time signatures
            
        Returns:
            str: Path to the saved file
        """
        # Clean composer name for filename
        clean_composer = re.sub(r'[^\w\s]', '', composer).replace(' ', '_').lower()
        filename = f"output/{clean_composer}_time_signatures.json"
        
        # Format for saving
        output_data = {composer: composer_data}
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved time signatures to {filename}")
        return filename
    
    def merge_with_imslp_data(self, imslp_file, composer, composer_data):
        """
        Merge extracted data with the existing IMSLP database
        
        Args:
            imslp_file (str): Path to the IMSLP JSON file
            composer (str): Composer name
            composer_data (dict): Dictionary of works with time signatures
            
        Returns:
            dict: Merged data
        """
        try:
            # Load IMSLP data
            with open(imslp_file, 'r', encoding='utf-8') as f:
                imslp_data = json.load(f)
            
            # Check if composer exists
            if composer not in imslp_data:
                print(f"\nComposer '{composer}' not found in IMSLP data. Adding as new entry.")
                imslp_data[composer] = {}
            
            # Track additions
            new_works = 0
            updated_works = 0
            new_movements = 0
            
            # Add works to IMSLP data
            for work_title, movements in composer_data.items():
                # Try to find a matching work
                best_match = None
                best_match_score = 0
                
                for imslp_title in imslp_data[composer].keys():
                    # Simple matching score based on common words
                    work_words = set(work_title.lower().split())
                    imslp_words = set(imslp_title.lower().split())
                    common_words = work_words.intersection(imslp_words)
                    
                    # Score based on percentage of common words
                    if len(work_words) > 0 and len(imslp_words) > 0:
                        match_score = len(common_words) / max(len(work_words), len(imslp_words))
                        
                        # Prefer matches with higher scores
                        if match_score > best_match_score and match_score > 0.3:  # At least 30% match
                            best_match = imslp_title
                            best_match_score = match_score
                
                if best_match:
                    print(f"\nMatched '{work_title}' to existing work '{best_match}'")
                    
                    # Add new movements
                    for movement in movements:
                        # Check if this time signature already exists
                        exists = False
                        for existing in imslp_data[composer][best_match]:
                            if existing['time_signature'] == movement['time_signature']:
                                # Update PDF link if not exists in existing
                                if 'pdf_link' not in existing and 'pdf_link' in movement and movement['pdf_link']:
                                    existing['pdf_link'] = movement['pdf_link']
                                    print(f"  Updated PDF link for {existing['movement']}")
                                exists = True
                                break
                        
                        if not exists:
                            imslp_data[composer][best_match].append(movement)
                            new_movements += 1
                            print(f"  Added movement: {movement['movement']} ({movement['time_signature']})")
                    
                    updated_works += 1
                else:
                    # Add as new work
                    imslp_data[composer][work_title] = movements
                    new_works += 1
                    new_movements += len(movements)
                    print(f"\nAdded new work: {work_title} with {len(movements)} movements")
            
            # Save merged data
            merged_file = f"output/imslp_scores_updated.json"
            with open(merged_file, 'w', encoding='utf-8') as f:
                json.dump(imslp_data, f, indent=2, ensure_ascii=False)
            
            print(f"\nMerged data saved to {merged_file}")
            print(f"Added {new_works} new works and {new_movements} new movements")
            print(f"Updated {updated_works} existing works")
            
            return imslp_data
            
        except Exception as e:
            print(f"Error merging with IMSLP data: {e}")
            return None
    
    def process_all_composers(self, imslp_file, max_works_per_composer=1000):
        """
        Process all available composers in the Kern database
        
        Args:
            imslp_file (str): Path to the IMSLP JSON file
            max_works_per_composer (int): Maximum works to process per composer
            
        Returns:
            dict: Dictionary with results for each composer
        """
        results = {}
        
        # Create a progress log file
        progress_log = f"output/all_composers_progress_{int(time.time())}.txt"
        with open(progress_log, 'w', encoding='utf-8') as f:
            f.write(f"Starting extraction of all composers at {time.ctime()}\n")
            f.write(f"Max works per composer: {max_works_per_composer}\n\n")
        
        # Process each composer
        for i, composer in enumerate(self.available_composers):
            try:
                print(f"\n\n{'='*50}")
                print(f"Processing composer {i+1}/{len(self.available_composers)}: {composer}")
                print(f"{'='*50}")
                
                # Log progress
                with open(progress_log, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*30}\n")
                    f.write(f"Starting {composer} at {time.ctime()}\n")
                
                # Process the composer
                composer_data = self.process_composer(composer, max_works_per_composer)
                
                # If data found, save and merge
                if composer_data:
                    # Save to separate file
                    file_path = self.save_composer_data(composer, composer_data)
                    
                    # Merge with IMSLP data
                    self.merge_with_imslp_data(imslp_file, composer, composer_data)
                    
                    # Store results
                    results[composer] = {
                        "works_found": len(composer_data),
                        "file_path": file_path
                    }
                    
                    # Log progress
                    with open(progress_log, 'a', encoding='utf-8') as f:
                        f.write(f"Completed {composer}: Found {len(composer_data)} works\n")
                else:
                    print(f"No data found for {composer}")
                    
                    # Log progress
                    with open(progress_log, 'a', encoding='utf-8') as f:
                        f.write(f"No data found for {composer}\n")
                
                # Wait between composers to avoid overloading the server
                time.sleep(3)
                
            except Exception as e:
                print(f"Error processing {composer}: {e}")
                
                # Log error
                with open(progress_log, 'a', encoding='utf-8') as f:
                    f.write(f"Error processing {composer}: {e}\n")
                
                # Continue with next composer
                continue
        
        # Log completion
        with open(progress_log, 'a', encoding='utf-8') as f:
            f.write(f"\nCompleted all composers at {time.ctime()}\n")
            f.write(f"Results: {json.dumps(results, indent=2)}\n")
        
        return results

def main():
    """Main function to run the script"""
    print("Enhanced Kern Humdrum Time Signature Extractor")
    print("=============================================")
    print("This script extracts time signatures from the Kern Humdrum database")
    print("and saves PDF links for each piece.")
    
    extractor = KernExtractor()
    
    # Options menu
    print("\nOptions:")
    print("1: Extract time signatures for a composer")
    print("2: Merge with imslp_scores_corrected.json")
    print("3: Extract and merge for ALL composers (limit 1000 works each)")
    print("4: Extract and merge for a SINGLE composer")
    print("5: Batch process multiple composers")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == "1":
        composer = input("\nEnter composer name (e.g., Bach, Beethoven): ")
        max_works_input = input("Maximum number of works to process (enter for all, 'all' for all): ")
        
        # Handle different input formats for max_works
        if not max_works_input.strip() or max_works_input.lower() == 'all':
            max_works = None
        else:
            try:
                max_works = int(max_works_input)
            except ValueError:
                print(f"Invalid input: '{max_works_input}'. Using default (all).")
                max_works = None
        
        composer_data = extractor.process_composer(composer, max_works)
        if composer_data:
            extractor.save_composer_data(composer, composer_data)
    
    elif choice == "2":
        composer = input("\nEnter composer name: ")
        composer_file = input("Enter path to extracted composer data JSON: ")
        imslp_file = input("Enter path to imslp_scores_corrected.json: ")
        
        try:
            # Load composer data
            with open(composer_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if composer in data:
                composer_data = data[composer]
                extractor.merge_with_imslp_data(imslp_file, composer, composer_data)
            else:
                print(f"Composer '{composer}' not found in {composer_file}")
        
        except Exception as e:
            print(f"Error loading files: {e}")
    
    elif choice == "3":
        print("\nThis will extract and merge data for ALL available composers in Kern.")
        print("Each composer will be limited to a maximum of 1000 works.")
        print("This will take a long time and generate a lot of data.")
        
        confirm = input("Are you sure you want to continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
        
        imslp_file = input("Enter path to imslp_scores_corrected.json: ")
        
        # Check if the file exists
        if not os.path.exists(imslp_file):
            print(f"Error: File '{imslp_file}' does not exist.")
            return
        
        print("\nStarting extraction for all composers...")
        print("Progress will be logged to output/all_composers_progress_[timestamp].txt")
        print("You can check this file for progress updates.")
        
        # Set debug flag to avoid creating too many files
        os.environ["KERN_DEBUG"] = "0"
        
        # Process all composers
        results = extractor.process_all_composers(imslp_file, 1000)
        
        # Print summary
        print("\n\nExtraction complete! Summary:")
        print(f"Processed {len(results)} composers")
        total_works = sum(result['works_found'] for result in results.values())
        print(f"Total works found: {total_works}")
        
        # Final merged file
        print(f"Final merged data saved to: output/imslp_scores_updated.json")
    
    elif choice == "4":
        composer = input("\nEnter composer name (e.g., Bach, Beethoven): ")
        imslp_file = input("Enter path to imslp_scores_corrected.json: ")
        max_works_input = input("Maximum number of works to process (enter for all, 'all' for all): ")
        
        # Handle different input formats for max_works
        if not max_works_input.strip() or max_works_input.lower() == 'all':
            max_works = None
        else:
            try:
                max_works = int(max_works_input)
            except ValueError:
                print(f"Invalid input: '{max_works_input}'. Using default (all).")
                max_works = None
        
        # Check if the IMSLP file exists
        if not os.path.exists(imslp_file):
            print(f"Error: File '{imslp_file}' does not exist.")
            return
        
        # Extract data
        composer_data = extractor.process_composer(composer, max_works)
        if composer_data:
            # Save extracted data
            extractor.save_composer_data(composer, composer_data)
            
            # Merge with IMSLP data
            extractor.merge_with_imslp_data(imslp_file, composer, composer_data)
    
    elif choice == "5":
        composers_input = input("\nEnter composer names separated by commas: ")
        composers = [c.strip() for c in composers_input.split(',')]
        
        imslp_file = input("Enter path to imslp_scores_corrected.json: ")
        max_works_input = input("Maximum works per composer (enter for all, 'all' for all): ")
        
        # Handle different input formats for max_works
        if not max_works_input.strip() or max_works_input.lower() == 'all':
            max_works = None
        else:
            try:
                max_works = int(max_works_input)
            except ValueError:
                print(f"Invalid input: '{max_works_input}'. Using default (all).")
                max_works = None
        
        # Check if the IMSLP file exists
        if not os.path.exists(imslp_file):
            print(f"Error: File '{imslp_file}' does not exist.")
            return
        
        for composer in composers:
            print(f"\n========== Processing {composer} ==========")
            composer_data = extractor.process_composer(composer, max_works)
            if composer_data:
                extractor.save_composer_data(composer, composer_data)
                extractor.merge_with_imslp_data(imslp_file, composer, composer_data)
    
    else:
        print("Invalid choice. Please run the script again with a valid option.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
