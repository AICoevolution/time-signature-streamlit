import json
import os
import pathlib
from music21 import corpus, converter, stream, meter, environment
import re

def setup_music21_environment():
    """Set up the music21 environment and ensure the corpus is properly configured"""
    print("Setting up music21 environment...")
    
    # Get environment object
    env = environment.Environment()
    
    # Check if we can access the corpus
    try:
        # Use getDefaultRootTempDir instead of getUserData
        corpus_path = env.getDefaultRootTempDir()
        print(f"music21 is looking for scores in: {corpus_path}")
        
        # Check corpus content
        corpus_items = list(corpus.corpora.CoreCorpus().getPaths())
        corpus_size = len(corpus_items)
        print(f"Found {corpus_size} items in the corpus.")
        
        if corpus_size < 10:
            print("The corpus appears to be empty or very small. Attempting to download...")
            download_corpus()
        else:
            print("Corpus looks good!")
            
        return True
    except Exception as e:
        print(f"Error checking corpus: {str(e)}")
        print("Attempting to download the corpus...")
        download_corpus()
        return False

def download_corpus():
    """Download the music21 corpus if not already present"""
    try:
        # Try to download the corpus using music21's built-in functions
        print("Downloading the music21 corpus...")
        
        corpus.corpora.CoreCorpus().download()
        
        print("Corpus downloaded successfully.")
        return True
    except Exception as e:
        print(f"Error downloading corpus: {str(e)}")
        print("Please manually download some scores and add them to music21's corpus.")
        print("You can do this by installing music21 and then running:")
        print("from music21 import corpus")
        print("corpus.corpora.CoreCorpus().download()")
        return False

def extract_time_signatures_from_corpus():
    """Extract time signatures from the music21 corpus"""
    
    print("Starting time signature extraction from music21 corpus...")
    
    # Create output dictionary
    output_data = {}
    
    # Get composers manually from the corpus
    composers = get_composers_from_corpus()
    
    if not composers:
        print("No composers found in the corpus. You may need to download the corpus first.")
        return {}
    
    print(f"Found {len(composers)} composers in the corpus.")
    
    # Process each composer
    for composer, works in composers.items():
        print(f"Processing works by {composer}...")
        
        # Map music21's composer names to standard names
        composer_map = {
            'bach': 'Johann Sebastian Bach',
            'beethoven': 'Ludwig van Beethoven',
            'mozart': 'Wolfgang Amadeus Mozart',
            'schumann': 'Robert Schumann',
            'chopin': 'Frédéric Chopin',
            'schubert': 'Franz Schubert',
            'handel': 'George Frideric Handel',
            'haydn': 'Joseph Haydn',
            'bwv': 'Johann Sebastian Bach',
            'schoenberg': 'Arnold Schoenberg',
            'joplin': 'Scott Joplin',
            'schumann_clara': 'Clara Schumann',
            'cpebach': 'Carl Philipp Emanuel Bach',
            'palestrina': 'Giovanni Pierluigi da Palestrina',
            'brahms': 'Johannes Brahms',
            'monteverdi': 'Claudio Monteverdi',
            'josquin': 'Josquin des Prez',
            'weber': 'Carl Maria von Weber'
        }
        
        composer_name = composer_map.get(composer, composer.title())
        if composer_name not in output_data:
            output_data[composer_name] = {}
        
        # Process each work
        for work_path in works:
            try:
                print(f"  Loading {work_path}...")
                work_path_str = str(work_path)  # Convert Path object to string if needed
                
                # Skip certain file types or collections
                if any(skip in work_path_str for skip in ['/_', '/demo', '/test', '.abc', '.xml']):
                    continue
                    
                # Load the score
                score = corpus.parse(work_path_str)
                
                # Extract work title
                filename = os.path.basename(work_path_str)
                title = clean_title(filename, composer)
                
                # Skip if we couldn't get a good title
                if not title or title == 'Unknown':
                    continue
                
                # Extract movements and their time signatures
                movements = extract_movements(score, title)
                
                # Only add if we have movements with time signatures
                if movements:
                    output_data[composer_name][title] = movements
                    print(f"  ✓ Added {title} with {len(movements)} movements")
                
            except Exception as e:
                print(f"  ✗ Error processing {work_path}: {str(e)}")
    
    # Save the data
    with open('music21_time_signatures.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Extraction complete. Data saved to music21_time_signatures.json")
    
    # Print summary stats
    total_works = sum(len(works) for works in output_data.values())
    total_movements = sum(sum(len(movements) for movements in composer_works.values()) 
                       for composer_works in output_data.values())
    
    print(f"Extracted {total_works} works with {total_movements} movements across {len(output_data)} composers.")
    
    return output_data

def get_composers_from_corpus():
    """Get composers and their works directly from the corpus"""
    composers = {}
    
    # These are the composers we expect to find in the corpus
    expected_composers = [
        'bach', 'beethoven', 'brahms', 'chopin', 'ciconia', 'corelli', 
        'cpebach', 'handel', 'haydn', 'josquin', 'luca', 'monteverdi', 
        'mozart', 'palestrina', 'schoenberg', 'schubert', 'schumann', 
        'weber'
    ]
    
    # Try to get works for each expected composer
    for composer_name in expected_composers:
        try:
            works = corpus.getComposer(composer_name)
            if works:
                composers[composer_name] = works
                print(f"Found {len(works)} works for {composer_name}")
        except Exception as e:
            print(f"Error finding works for {composer_name}: {str(e)}")
    
    # If the above method didn't work, try an alternative approach
    if not composers:
        print("Trying alternative method to find composers...")
        
        # Get all paths in the corpus
        all_paths = list(corpus.corpora.CoreCorpus().getPaths())
        
        # Extract composer names from paths
        for path in all_paths:
            path_str = str(path)
            parts = path_str.split(os.sep)
            if len(parts) > 1:
                potential_composer = parts[0].lower()
                if potential_composer not in composers:
                    composers[potential_composer] = []
                composers[potential_composer].append(path)
    
    return composers

def clean_title(filename, composer):
    """Extract a clean title from the filename"""
    
    # Remove file extension
    title = os.path.splitext(filename)[0]
    
    # Handle specific composers
    if composer == 'beethoven':
        # For Beethoven's sonatas and symphonies
        if 'opus' in title.lower() or 'op' in title.lower():
            # Extract opus information
            opus_match = re.search(r'op\.?\s*(\d+)(?:no\.?\s*(\d+))?', title, re.IGNORECASE)
            if opus_match:
                opus_num = opus_match.group(1)
                sonata_num = opus_match.group(2) if opus_match.group(2) else None
                
                if 'sonata' in title.lower():
                    # Map opus to sonata number
                    opus_to_sonata = {
                        '2': ['1', '2', '3'],  # Op. 2 has three sonatas
                        '10': ['5', '6', '7'],
                        '14': ['9', '10'],
                        '31': ['16', '17', '18'],
                        '49': ['19', '20'],
                        '27': ['13', '14'],  # Includes "Moonlight" Sonata
                    }
                    
                    if opus_num in opus_to_sonata and sonata_num:
                        try:
                            sonata_index = int(sonata_num) - 1
                            if sonata_index < len(opus_to_sonata[opus_num]):
                                actual_num = opus_to_sonata[opus_num][sonata_index]
                                nickname = ""
                                
                                # Add nicknames for famous sonatas
                                if opus_num == '27' and sonata_num == '2':
                                    nickname = ' ("Moonlight")'
                                elif opus_num == '53':
                                    nickname = ' ("Waldstein")'
                                elif opus_num == '57':
                                    nickname = ' ("Appassionata")'
                                
                                return f"Piano Sonata No. {actual_num} in {get_key(title)}, Op. {opus_num} No. {sonata_num}{nickname}"
                        except (ValueError, IndexError):
                            pass
                    
                    return f"Piano Sonata Op. {opus_num}" + (f" No. {sonata_num}" if sonata_num else "")
                
                elif 'symphony' in title.lower():
                    return f"Symphony No. {get_symphony_number(title)} in {get_key(title)}"
        
        # For other Beethoven works
        if 'sonata' in title.lower():
            num_match = re.search(r'no\.?\s*(\d+)', title, re.IGNORECASE)
            if num_match:
                num = num_match.group(1)
                return f"Piano Sonata No. {num} in {get_key(title)}"
            
        if 'symphony' in title.lower():
            return f"Symphony No. {get_symphony_number(title)} in {get_key(title)}"
    
    elif composer == 'mozart':
        # For Mozart's K. numbering
        k_match = re.search(r'k\.?\s*(\d+)', title, re.IGNORECASE)
        if k_match:
            k_num = k_match.group(1)
            
            if 'symphony' in title.lower():
                sym_num = get_symphony_number(title)
                if sym_num:
                    return f"Symphony No. {sym_num} in {get_key(title)}, K. {k_num}"
                else:
                    return f"Symphony in {get_key(title)}, K. {k_num}"
            
            if 'sonata' in title.lower():
                return f"Piano Sonata in {get_key(title)}, K. {k_num}"
    
    elif composer == 'bach':
        # For Bach's BWV numbering
        bwv_match = re.search(r'bwv\.?\s*(\d+)', title, re.IGNORECASE)
        if bwv_match:
            bwv_num = bwv_match.group(1)
            
            if 'prelude' in title.lower() and 'fugue' in title.lower():
                return f"Prelude and Fugue in {get_key(title)}, BWV {bwv_num}"
            
            if 'brandenburg' in title.lower() or 'concerto' in title.lower():
                concerto_num = re.search(r'no\.?\s*(\d+)', title, re.IGNORECASE)
                if concerto_num:
                    num = concerto_num.group(1)
                    return f"Brandenburg Concerto No. {num} in {get_key(title)}, BWV {bwv_num}"
    
    # If we couldn't extract a structured title, clean up the filename
    title = re.sub(r'[_-]', ' ', title)
    title = ' '.join(w.capitalize() for w in title.split())
    
    return title

def get_key(title):
    """Extract key from title"""
    
    # Dictionary mapping common key terms to standardized format
    key_map = {
        'cmajor': 'C major',
        'cminor': 'C minor',
        'c-major': 'C major',
        'c-minor': 'C minor',
        'c_major': 'C major',
        'c_minor': 'C minor',
        'c major': 'C major',
        'c minor': 'C minor',
        'dmajor': 'D major',
        'dminor': 'D minor',
        'ebmajor': 'E-flat major',
        'ebminor': 'E-flat minor',
        'emajor': 'E major',
        'eminor': 'E minor',
        'fmajor': 'F major',
        'fminor': 'F minor',
        'gmajor': 'G major',
        'gminor': 'G minor',
        'amajor': 'A major',
        'aminor': 'A minor',
        'bbmajor': 'B-flat major',
        'bbminor': 'B-flat minor',
        'bmajor': 'B major',
        'bminor': 'B minor',
    }
    
    title_lower = title.lower()
    
    # Try to find a key in the title
    for key_term, formatted_key in key_map.items():
        if key_term in title_lower.replace(' ', ''):
            return formatted_key
    
    # Special patterns like D-Dur, c-moll (German style)
    german_key_match = re.search(r'([a-g])-(dur|moll)', title_lower)
    if german_key_match:
        note = german_key_match.group(1).upper()
        mode = 'major' if german_key_match.group(2) == 'dur' else 'minor'
        return f"{note} {mode}"
    
    # Look for common patterns like "in D", "in C minor", etc.
    key_match = re.search(r'in\s+([A-G](?:\-?flat|\-?sharp)?)\s*(major|minor)?', title, re.IGNORECASE)
    if key_match:
        note = key_match.group(1)
        mode = key_match.group(2) or "major"  # Default to major if not specified
        return f"{note} {mode.lower()}"
    
    # If no key found, try to determine from the music analysis (beyond scope here)
    return "Unknown key"

def get_symphony_number(title):
    """Extract symphony number from title"""
    
    # Try to find a number after "symphony" or "no."
    sym_match = re.search(r'symphony\s*(?:no\.?)?\s*(\d+)', title, re.IGNORECASE)
    if sym_match:
        return sym_match.group(1)
    
    # Try to find just a number
    num_match = re.search(r'no\.?\s*(\d+)', title, re.IGNORECASE)
    if num_match:
        return num_match.group(1)
    
    return "Unknown"

def extract_movements(score, title):
    """Extract movements and their time signatures from a music21 score"""
    
    movements = []
    
    # Check if the score is a multi-movement work
    if isinstance(score, stream.Score) and score.iter().getElementsByClass('Score'):
        # Multi-movement work
        movement_scores = list(score.iter().getElementsByClass('Score'))
        
        for i, movement_score in enumerate(movement_scores):
            # Try to get movement title
            movement_title = None
            for metadata in movement_score.iter().getElementsByClass('Metadata'):
                if hasattr(metadata, 'movementName') and metadata.movementName:
                    movement_title = metadata.movementName
                    break
            
            # Fallback to a generic movement title
            if not movement_title:
                # Use roman numerals for movement numbers
                roman_nums = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
                roman = roman_nums[i] if i < len(roman_nums) else str(i+1)
                
                # Try to determine a tempo marking
                tempo_marks = []
                for tempo in movement_score.iter().getElementsByClass('TempoIndication'):
                    if hasattr(tempo, 'text') and tempo.text:
                        tempo_marks.append(tempo.text)
                
                tempo_text = ', '.join(tempo_marks) if tempo_marks else "Allegro"  # Default if none found
                movement_title = f"{roman}. {tempo_text}"
            
            # Get time signature
            time_sig = get_time_signature(movement_score)
            
            if time_sig:
                movements.append({
                    "movement": movement_title,
                    "time_signature": time_sig
                })
    else:
        # Single movement work (or work without explicit movement divisions)
        time_sig = get_time_signature(score)
        
        # Get title from metadata if available
        movement_title = "I. Allegro"  # Default
        if score.metadata and hasattr(score.metadata, 'movementName') and score.metadata.movementName:
            movement_title = "I. " + score.metadata.movementName
        
        if time_sig:
            movements.append({
                "movement": movement_title,
                "time_signature": time_sig
            })
    
    return movements

def get_time_signature(score):
    """Extract the primary time signature from a score"""
    
    # Look for explicit time signatures
    time_sigs = score.flat.getElementsByClass('TimeSignature')
    if time_sigs:
        # Get the first time signature
        return f"{time_sigs[0].numerator}/{time_sigs[0].denominator}"
    
    # Try to determine from measure structure
    measures = score.getElementsByClass('Measure')
    if measures and len(measures) > 3:  # Need a few measures to guess
        # Analyze the first few measures to guess the time signature
        beat_counts = [len(m.getElementsByClass('Note')) for m in measures[:5]]
        if all(count == beat_counts[0] for count in beat_counts) and beat_counts[0] > 0:
            # Simple time signature based on note count (very approximate)
            return f"{beat_counts[0]}/4"
    
    # Default if we can't determine
    return "4/4"  # Most common classical time signature

def merge_with_existing_data(new_data, existing_data_path):
    """Merge newly extracted data with existing database, prioritizing manual corrections"""
    
    try:
        with open(existing_data_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"Error loading existing data: {str(e)}")
        existing_data = {}
    
    # Create a merged dataset
    merged_data = existing_data.copy()
    
    # Add new data where it doesn't exist in the original
    for composer, works in new_data.items():
        if composer not in merged_data:
            merged_data[composer] = {}
        
        for work_title, movements in works.items():
            # Skip if work already exists (preserve manual corrections)
            if work_title not in merged_data[composer]:
                merged_data[composer][work_title] = movements
    
    # Save merged data
    output_path = 'expanded_time_signatures.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"Merged data saved to {output_path}")
    
    # Statistics
    old_works = sum(len(works) for works in existing_data.values())
    new_works = sum(len(works) for works in merged_data.values()) - old_works
    print(f"Added {new_works} new works to the existing {old_works} works.")
    
    return merged_data

def test_extraction():
    """Run a test extraction on a limited set of composers/works"""
    print("Running test extraction...")
    
    # Create output dictionary
    output_data = {}
    
    # Test with just a few composers
    test_composers = ['beethoven', 'mozart', 'bach']
    
    for composer_name in test_composers:
        print(f"Trying to find works by {composer_name}...")
        
        try:
            # Get works for this composer
            works = corpus.getComposer(composer_name)
            
            if not works:
                print(f"No works found for {composer_name}")
                continue
                
            print(f"Found {len(works)} works for {composer_name}")
            
            # Take just a few works for testing
            test_works = works[:3]
            
            # Map to standard composer names
            composer_map = {
                'bach': 'Johann Sebastian Bach',
                'beethoven': 'Ludwig van Beethoven',
                'mozart': 'Wolfgang Amadeus Mozart',
            }
            
            full_composer_name = composer_map.get(composer_name, composer_name.title())
            output_data[full_composer_name] = {}
            
            # Process each work
            for work_path in test_works:
                try:
                    print(f"  Processing {work_path}...")
                    
                    # Convert path to string if needed
                    work_path_str = str(work_path)
                    
                    # Load the score
                    score = corpus.parse(work_path_str)
                    
                    # Extract work title
                    filename = os.path.basename(work_path_str)
                    title = clean_title(filename, composer_name)
                    
                    # Extract movements
                    movements = extract_movements(score, title)
                    
                    if movements:
                        output_data[full_composer_name][title] = movements
                        print(f"  ✓ Added {title} with {len(movements)} movements")
                    else:
                        print(f"  ✗ No movements found for {title}")
                
                except Exception as e:
                    print(f"  ✗ Error processing {work_path}: {str(e)}")
        
        except Exception as e:
            print(f"Error getting works for {composer_name}: {str(e)}")
    
    # Save test data
    with open('test_extraction.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Test extraction complete. Data saved to test_extraction.json")
    
    # Print summary
    total_works = sum(len(works) for works in output_data.values())
    total_movements = sum(sum(len(movements) for movements in composer_works.values()) 
                       for composer_works in output_data.values())
    
    print(f"Extracted {total_works} works with {total_movements} movements across {len(output_data)} composers.")
    
    return output_data

if __name__ == "__main__":
    print("Music21 Time Signature Extractor (Updated for v9.5.0)")
    print("====================================================")
    print("Options:")
    print("1: Check and setup music21 environment")
    print("2: Run a test extraction (few works)")
    print("3: Run full extraction")
    print("4: Merge existing JSON files")
    
    while True:
        choice = input("Enter your choice (1, 2, 3, or 4): ")
        if choice in ['1', '2', '3', '4']:
            break
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    if choice == '1':
        # Check environment and corpus setup
        setup_music21_environment()
    
    elif choice == '2':
        # Run a limited test extraction
        setup_music21_environment()
        test_extraction()
    
    elif choice == '3':
        # Run full extraction
        setup_music21_environment()
        new_data = extract_time_signatures_from_corpus()
        
        # Ask if user wants to merge with existing data
        merge_choice = input("Do you want to merge with existing data? (y/n): ")
        if merge_choice.lower() == 'y':
            existing_path = input("Enter path to existing JSON file (full path including filename): ")
            merge_with_existing_data(new_data, existing_path)
    
    else:
        # Merge existing data
        new_path = input("Enter path to new JSON file (full path including filename): ")
        if not new_path.endswith('.json'):
            new_path += '.json'
            
        existing_path = input("Enter path to existing JSON file (full path including filename): ")
        if not existing_path.endswith('.json'):
            existing_path += '.json'
        
        try:
            with open(new_path, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
            merge_with_existing_data(new_data, existing_path)
        except Exception as e:
            print(f"Error: {str(e)}")
