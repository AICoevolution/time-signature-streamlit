import streamlit as st
import difflib
import json
import urllib.parse
import random
import re

# === Load IMSLP JSON Database ===
def load_imslp_database(path='imslp_scores_corrected.json'):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load IMSLP data: {e}")
        return {}

# === Improved Search Function ===
def search_works(query, imslp_db, max_results=10):
    if not query or not imslp_db:
        return []
    
    query = query.lower().strip()
    results = []
    
    # Extract composer and work information if possible
    composer_match = None
    work_type_match = None
    number_match = None
    
    # Common composer names
    composers = [c.lower() for c in imslp_db.keys()]
    composer_match = next((c for c in composers if c.lower() in query), None)
    
    # Common work types
    work_types = ["symphony", "sonata", "concerto", "quartet", "nocturne", "etude", "prelude"]
    work_type_match = next((wt for wt in work_types if wt in query), None)
    
    # Look for numbers (both digits and spelled out)
    number_patterns = [
        r'\b(\d+)\b',  # Numbers like 5, 40
        r'\bno\.?\s*(\d+)\b',  # No. 5, No 5
        r'\bnumber\s*(\d+)\b',  # Number 5
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b'  # Spelled out
    ]
    
    for pattern in number_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            number_match = match.group(1)
            if number_match in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']:
                # Convert spelled numbers to digits
                number_words = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 
                               'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
                               'eleven': '11', 'twelve': '12'}
                number_match = number_words[number_match]
            break
    
    # Search through database with smarter matching
    for composer, works in imslp_db.items():
        # Skip if a composer was specified and doesn't match
        if composer_match and composer_match not in composer.lower():
            continue
            
        for work_title in works:
            # Calculate match score based on multiple factors
            score = 0
            
            # If work type matches (symphony, sonata, etc)
            if work_type_match and work_type_match in work_title.lower():
                score += 3
            
            # If number matches exactly (like "Symphony No. 5" or "Symphony No. 40")
            if number_match:
                number_in_title = re.search(r'No\.\s*(\d+)|Number\s*(\d+)|\bNo\s*(\d+)|\b(\d+)\b', work_title)
                if number_in_title:
                    # Get the matched number regardless of which group captured it
                    title_number = next(g for g in number_in_title.groups() if g is not None)
                    if title_number == number_match:
                        score += 5
                    # Partial number match (for double-digit numbers)
                    elif number_match in title_number:
                        score += 2
            
            # Overall text similarity
            text_similarity = difflib.SequenceMatcher(None, query, f"{composer} {work_title}".lower()).ratio()
            score += text_similarity * 2
            
            # Add to results if score is significant
            if score > 0.5:
                results.append({
                    "composer": composer,
                    "work": work_title,
                    "movements": works[work_title],
                    "score": score
                })
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]

# === Get Movements by Time Signature ===
def get_movements_by_time_signature(imslp_db, time_signature):
    results = []
    for composer, works in imslp_db.items():
        for work_title, movements in works.items():
            for movement in movements:
                if movement["time_signature"] == time_signature:
                    results.append({
                        "composer": composer,
                        "work": work_title,
                        "movement": movement["movement"],
                        "time_signature": movement["time_signature"]
                    })
    return results

# === Streamlit UI ===
st.set_page_config(page_title="Classical Time Signature Lookup", layout="wide")
st.title("🎵 Classical Time Signature Lookup")

# Load database
imslp_db = load_imslp_database()

# Create tabs for different functions
tab1, tab2 = st.tabs(["🔍 Search Works", "🎲 Random by Time Signature"])

with tab1:
    st.markdown("""
    Search for a classical work by composer, work type, and/or number:
    - Examples: "Mozart Symphony 40", "Beethoven Sonata Moonlight", "Bach Brandenburg 3"
    """)
    
    query = st.text_input("Enter Work Title:", key="search_query")
    
    if query:
        results = search_works(query, imslp_db)
        
        if results:
            st.success(f"Found {len(results)} matching works")
            
            # Display results in a more compact format
            for i, result in enumerate(results):
                with st.expander(f"{result['composer']}: {result['work']}", expanded=(i==0)):
                    # Create columns for a more compact display
                    col1, col2 = st.columns([3, 1])
                    
                    # Display movements in first column
                    with col1:
                        for mv in result["movements"]:
                            st.markdown(f"**{mv['movement']}** — `{mv['time_signature']}`")
                    
                    # Display external links in second column
                    with col2:
                        query_encoded = urllib.parse.quote(f"{result['work']} {result['composer']}")
                        spotify_url = f"https://open.spotify.com/search/{query_encoded}"
                        imslp_url = f"https://www.google.com/search?q=site%3Aimslp.org+score+pdf+{query_encoded}"
                        youtube_url = f"https://www.youtube.com/results?search_query={query_encoded}"
                        
                        st.markdown("### Links")
                        st.markdown(f"[🎧 Spotify]({spotify_url})")
                        st.markdown(f"[📜 Score]({imslp_url})")
                        st.markdown(f"[▶️ YouTube]({youtube_url})")
        else:
            st.warning("No matches found. Try a different search term.")

with tab2:
    st.markdown("### 🎲 Find Random Works by Time Signature")
    
    # Get unique time signatures
    unique_signatures = set()
    for composer, works in imslp_db.items():
        for work in works.values():
            for movement in work:
                unique_signatures.add(movement["time_signature"])
    
    time_signatures_list = sorted(list(unique_signatures))
    
    selected_signature = st.selectbox("Select Time Signature:", time_signatures_list)
    
    st.markdown(f"### Works in {selected_signature} Time")
    
    if st.button("Show Me 5 Random Examples"):
        matching_movements = get_movements_by_time_signature(imslp_db, selected_signature)
        
        if matching_movements:
            # Select 5 random movements, or all if less than 5
            samples = random.sample(matching_movements, min(5, len(matching_movements)))
            
            # Display in a nice format
            for i, sample in enumerate(samples):
                st.markdown(f"""
                {i+1}. **{sample['composer']}**: {sample['work']}  
                   *{sample['movement']}* ({sample['time_signature']})
                """)
        else:
            st.warning(f"No works found with {selected_signature} time signature.")

# === Sidebar ===
with st.sidebar:
    st.markdown("### ℹ️ About This Tool")
    st.write("Search classical works and get movement time signatures, plus links to listen or read the score.")
    
    # Add time signature distribution
    st.markdown("### 📊 Time Signature Distribution")
    signature_counts = {}
    for composer, works in imslp_db.items():
        for work in works.values():
            for movement in work:
                sig = movement["time_signature"]
                if sig in signature_counts:
                    signature_counts[sig] += 1
                else:
                    signature_counts[sig] = 1
    
    # Sort by frequency, descending
    sorted_sigs = sorted(signature_counts.items(), key=lambda x: x[1], reverse=True)
    
    for sig, count in sorted_sigs:
        st.text(f"{sig}: {count} movements")
