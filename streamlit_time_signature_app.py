import streamlit as st
import difflib
import json
import urllib.parse
import random
import re
import pandas as pd
import altair as alt
import requests
from bs4 import BeautifulSoup

# =============================================
# === Configure Page and Custom CSS Styling ===
# =============================================
st.set_page_config(
    page_title="Classical Time Signature Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fixed header and compact layout
st.markdown("""
<style>
    /* Top header customization */
    .main-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: white;
        padding: 10px 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 10px;
    }
    
    /* Make page title smaller and more compact */
    h1 {
        font-size: 2rem !important;
        margin-top: -15px !important;
        margin-bottom: 0px !important;
    }
    
    /* Make tabs sticky */
    .stTabs [data-baseweb="tab-list"] {
        position: sticky;
        top: 60px;
        z-index: 998;
        background-color: white;
        padding: 2px 0;
    }
    
    /* Result cards styling */
    .result-card {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f9f9f9;
    }
    
    .movement-item {
        margin: 5px 0;
        padding: 5px 0;
        border-bottom: 1px dotted #e0e0e0;
    }
    
    .time-signature {
        font-family: monospace;
        background-color: #f0f0f0;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: bold;
        color: #d63384;
    }
    
    /* Media integration */
    .media-container {
        display: flex;
        margin-top: 10px;
    }
    
    .media-container > div {
        flex: 1;
        padding: 5px;
    }
    
    .media-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    
    /* Make expander headers more compact */
    .streamlit-expanderHeader {
        font-size: 1rem !important;
        padding: 0.5rem !important;
    }
    
    /* Compact sidebar */
    .css-1oe6wy4 {
        padding-top: 2rem;
    }
    
    /* Audio player styling */
    .audio-player {
        background-color: #f0f0f0;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =================================
# === YouTube Audio Player Code ===
# =================================
def youtube_audio_player(query, use_direct_video=False, height=90):
    """
    Creates a YouTube audio-only player by stripping video elements.
    
    Parameters:
        query: The search query for YouTube
        use_direct_video: Try to get a specific video instead of search results
        height: Height of the player (default: 90px)
    
    Returns:
        HTML component that plays only audio from YouTube
    """
    
    # Encode the search query for URL
    encoded_query = urllib.parse.quote(query)
    
    # Try to get a specific video ID first if requested
    video_id = None
    if use_direct_video:
        video_id = fetch_first_youtube_video_id(query)
    
    if video_id:
        # If we have a specific video ID, use it
        html = f"""
        <div class="audio-player">
            <iframe id="youtube-audio" 
                width="100%" 
                height="{height}" 
                src="https://www.youtube.com/embed/{video_id}?autoplay=0&controls=1&showinfo=0&modestbranding=1&rel=0&iv_load_policy=3&fs=0" 
                frameborder="0" 
                allow="accelerometer; autoplay; encrypted-media; gyroscope;" 
                style="border-radius: 4px;">
            </iframe>
            <div style="font-size: 0.8em; text-align: right; padding-right: 5px;">
                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank">
                    Open in YouTube
                </a>
            </div>
        </div>
        """
    else:
        # Otherwise use search results
        html = f"""
        <div class="audio-player">
            <iframe id="youtube-audio" 
                width="100%" 
                height="{height}" 
                src="https://www.youtube.com/embed?listType=search&list={encoded_query}&autoplay=0&controls=1&showinfo=0&modestbranding=1&rel=0&iv_load_policy=3&fs=0" 
                frameborder="0" 
                allow="accelerometer; autoplay; encrypted-media; gyroscope;" 
                style="border-radius: 4px;">
            </iframe>
            <div style="font-size: 0.8em; text-align: right; padding-right: 5px;">
                <a href="https://www.youtube.com/results?search_query={encoded_query}" target="_blank">
                    More on YouTube
                </a>
            </div>
        </div>
        """
    return html

def fetch_first_youtube_video_id(query):
    """
    Attempts to fetch the first YouTube video ID for a given search query.
    This is a more advanced approach but may break if YouTube changes their page structure.
    """
    try:
        # Create search URL
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        
        # Add a user agent to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            # Use regex to find video IDs in the page content
            video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
            
            if video_ids:
                return video_ids[0]  # Return the first match
    except Exception as e:
        st.error(f"Error fetching YouTube data: {str(e)}")
    
    return None

# ===============================
# === Database Loading & Cache ===
# ===============================
@st.cache_data
def load_imslp_database(path='imslp_scores_corrected.json'):
    """Load and cache the IMSLP database"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load IMSLP data: {e}")
        return {}

# ===========================
# === Search Functionality ===
# ===========================
def search_works(query, imslp_db, max_results=10):
    """Enhanced search function with smarter matching"""
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
    
    # Also handle common nickname-based searches like "moonlight", "pathetique", etc.
    nicknames = {
        "moonlight": ("Ludwig van Beethoven", "Piano Sonata No. 14 in C-sharp minor, Op. 27 No. 2"),
        "pathetique": ("Ludwig van Beethoven", "Piano Sonata No. 8 in C minor, Op. 13"),
        "waldstein": ("Ludwig van Beethoven", "Piano Sonata No. 21 in C major, Op. 53"),
        "appassionata": ("Ludwig van Beethoven", "Piano Sonata No. 23 in F minor, Op. 57"),
        "jupiter": ("Wolfgang Amadeus Mozart", "Symphony No. 41 in C major, K. 551"),
        "eroica": ("Ludwig van Beethoven", "Symphony No. 3 in E-flat major, Op. 55"),
        "pastoral": ("Ludwig van Beethoven", "Symphony No. 6 in F major, Op. 68"),
        "surprise": ("Joseph Haydn", "Symphony No. 94 in G major, Hob. I:94"),
        "unfinished": ("Franz Schubert", "Symphony No. 8 in B minor, D. 759")
    }
    
    for nickname, (composer, work) in nicknames.items():
        if nickname in query.lower():
            if composer in imslp_db and work in imslp_db[composer]:
                return [{
                    "composer": composer,
                    "work": work,
                    "movements": imslp_db[composer][work],
                    "score": 10  # High score for exact nickname match
                }]
    
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
                    title_number = next((g for g in number_in_title.groups() if g is not None), None)
                    if title_number and title_number == number_match:
                        score += 5
                    # Partial number match (for double-digit numbers)
                    elif title_number and number_match in title_number:
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

# =============================
# === Time Signature Methods ===
# =============================
def get_movements_by_time_signature(imslp_db, time_signature):
    """Find all movements with a specific time signature"""
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

def get_unique_time_signatures(imslp_db):
    """Get a sorted list of all unique time signatures in the database"""
    signatures = set()
    for composer, works in imslp_db.items():
        for work in works.values():
            for movement in work:
                signatures.add(movement["time_signature"])
    return sorted(list(signatures))

# ==============================
# === Visualization Methods ===
# ==============================
def create_time_signature_visualizations(imslp_db):
    """Create visualizations for time signature analysis"""
    # Collect data for visualization
    data = []
    for composer, works in imslp_db.items():
        for work_title, movements in works.items():
            for movement in movements:
                data.append({
                    'composer': composer,
                    'work': work_title,
                    'movement': movement['movement'],
                    'time_signature': movement['time_signature']
                })
    
    # Convert to DataFrame for easy manipulation
    df = pd.DataFrame(data)
    
    # Overall time signature distribution
    sig_counts = df['time_signature'].value_counts().reset_index()
    sig_counts.columns = ['time_signature', 'count']
    
    # Create interactive bar chart
    chart = alt.Chart(sig_counts).mark_bar().encode(
        x=alt.X('time_signature:N', sort='-y', title='Time Signature'),
        y=alt.Y('count:Q', title='Number of Movements'),
        color=alt.Color('time_signature:N', legend=None),
        tooltip=['time_signature', 'count']
    ).properties(
        width=600,
        height=400,
        title='Distribution of Time Signatures in Classical Works'
    ).interactive()
    
    # Get top composers (by number of works)
    top_composers = df['composer'].value_counts().nlargest(8).index.tolist()
    
    # Filter for top composers
    composer_df = df[df['composer'].isin(top_composers)]
    
    # Group by composer and time signature to count movements
    composer_counts = composer_df.groupby(['composer', 'time_signature']).size().reset_index(name='count')
    
    # Create heatmap
    heatmap = alt.Chart(composer_counts).mark_rect().encode(
        x=alt.X('time_signature:N', title='Time Signature'),
        y=alt.Y('composer:N', title='Composer'),
        color=alt.Color('count:Q', scale=alt.Scale(scheme='viridis'), title='Number of Movements'),
        tooltip=['composer', 'time_signature', 'count']
    ).properties(
        width=600,
        height=400,
        title='Time Signature Usage by Major Composers'
    ).interactive()
    
    return chart, heatmap

def create_comparison_chart(imslp_db, sig1, sig2):
    """Create a chart comparing usage of two time signatures"""
    # Collect data for selected signatures
    compare_data = []
    for composer, works in imslp_db.items():
        sig1_count = 0
        sig2_count = 0
        
        for work in works.values():
            for movement in work:
                if movement["time_signature"] == sig1:
                    sig1_count += 1
                elif movement["time_signature"] == sig2:
                    sig2_count += 1
        
        # Only include composers who have at least one movement in either signature
        if sig1_count > 0 or sig2_count > 0:
            compare_data.append({"composer": composer, "signature": sig1, "count": sig1_count})
            compare_data.append({"composer": composer, "signature": sig2, "count": sig2_count})
    
    # Convert to DataFrame
    compare_df = pd.DataFrame(compare_data)
    
    # Filter to top composers by total count for readability
    top_composers = compare_df.groupby('composer')['count'].sum().nlargest(10).index.tolist()
    compare_df = compare_df[compare_df['composer'].isin(top_composers)]
    
    # Create grouped bar chart
    comparison_chart = alt.Chart(compare_df).mark_bar().encode(
        x=alt.X('composer:N', sort='-y', title='Composer'),
        y=alt.Y('count:Q', title='Number of Movements'),
        color=alt.Color('signature:N', title='Time Signature'),
        tooltip=['composer', 'signature', 'count']
    ).properties(
        width=600,
        height=400,
        title=f'Comparison: {sig1} vs {sig2} Usage by Top Composers'
    ).interactive()
    
    return comparison_chart

# =======================
# === Main Application ===
# =======================
def main():
    # Fixed header at the top
    with st.container():
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.title("🎵 Classical Time Signature Explorer")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load database
    imslp_db = load_imslp_database()
    
    # Get unique time signatures for later use
    time_signatures_list = get_unique_time_signatures(imslp_db)
    
    # Create main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Search Works", "🎲 Random by Time Signature", "📊 Visualizations"])
    
    # ========================
    # === Search Works Tab ===
    # ========================
    with tab1:
        st.markdown("""
        Search for a classical work by composer, work type, number, or nickname:
        - Examples: "Mozart Symphony 40", "Beethoven Moonlight Sonata", "Bach Brandenburg 3"
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input("Enter Work Title:", key="search_query")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            search_button = st.button("Search", key="search_button", use_container_width=True)
        
        if query and (search_button or 'last_query' not in st.session_state or st.session_state.last_query != query):
            st.session_state.last_query = query
            
            with st.spinner("Searching..."):
                results = search_works(query, imslp_db)
            
            if results:
                st.success(f"Found {len(results)} matching works")
                
                # Display results in a more compact format
                for i, result in enumerate(results):
                    with st.expander(f"**{result['composer']}**: {result['work']}", expanded=(i==0)):
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        
                        # Movements section
                        for mv in result["movements"]:
                            st.markdown(
                                f"<div class='movement-item'>{mv['movement']} — "
                                f"<span class='time-signature'>{mv['time_signature']}</span></div>", 
                                unsafe_allow_html=True
                            )
                        
                        # Media integration section - Audio player and Score
                        st.markdown("<div class='media-container'>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("<h4>🎧 Listen</h4>", unsafe_allow_html=True)
                            search_term = f"{result['composer']} {result['work']}"
                            st.components.v1.html(youtube_audio_player(search_term), height=120)
                        
                        with col2:
                            st.markdown("<h4>📜 Score</h4>", unsafe_allow_html=True)
                            search_term = f"{result['composer']} {result['work']} score"
                            encoded_query = urllib.parse.quote(f"site:imslp.org {search_term}")
                            search_url = f"https://www.google.com/search?q={encoded_query}"
                            st.markdown(f"""
                            <div style="text-align: center; margin-top: 20px;">
                                <a href="{search_url}" target="_blank" style="text-decoration: none;">
                                    <button style="padding: 10px 20px; background-color: #4CAF50; color: white; 
                                                  border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                                        View Score on IMSLP
                                    </button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # External links
                        st.markdown("<div class='media-buttons'>", unsafe_allow_html=True)
                        query_encoded = urllib.parse.quote(f"{result['work']} {result['composer']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            spotify_url = f"https://open.spotify.com/search/{query_encoded}"
                            st.markdown(f"[🎧 Listen on Spotify]({spotify_url})")
                        
                        with col2:
                            youtube_url = f"https://www.youtube.com/results?search_query={query_encoded}"
                            st.markdown(f"[▶️ Watch on YouTube]({youtube_url})")
                        
                        with col3:
                            imslp_url = f"https://www.google.com/search?q=site%3Aimslp.org+score+pdf+{query_encoded}"
                            st.markdown(f"[📜 View Full Score]({imslp_url})")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No matches found. Try a different search term.")
    
    # ==================================
    # === Random by Time Signature Tab ===
    # ==================================
    with tab2:
        st.markdown("### 🎲 Find Random Works by Time Signature")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_signature = st.selectbox("Select Time Signature:", time_signatures_list)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            random_button = st.button("Show 5 Random Examples", use_container_width=True)
        
        st.markdown(f"### Works in {selected_signature} Time")
        
        if random_button or 'last_signature' not in st.session_state or st.session_state.last_signature != selected_signature:
            st.session_state.last_signature = selected_signature
            
            with st.spinner("Finding examples..."):
                matching_movements = get_movements_by_time_signature(imslp_db, selected_signature)
            
            if matching_movements:
                # Select 5 random movements, or all if less than 5
                samples = random.sample(matching_movements, min(5, len(matching_movements)))
                
                # Display in a nice format
                for i, sample in enumerate(samples):
                    st.markdown(f"<div class='result-card'>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <h3>{sample['composer']}</h3>
                    <p>{sample['work']}</p>
                    <div class='movement-item'>
                        {sample['movement']} — <span class='time-signature'>{sample['time_signature']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Media integration
                    search_term = f"{sample['composer']} {sample['work']} {sample['movement']}"
                    st.components.v1.html(youtube_audio_player(search_term), height=120)
                    
                    query_encoded = urllib.parse.quote(f"{sample['work']} {sample['composer']}")
                    imslp_url = f"https://www.google.com/search?q=site%3Aimslp.org+score+pdf+{query_encoded}"
                    st.markdown(f"[📜 View Score]({imslp_url})")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning(f"No works found with {selected_signature} time signature.")
    
    # ============================
    # === Visualizations Tab ===
    # ============================
    with tab3:
        st.markdown("### 📊 Time Signature Analysis")
        
        # Create and display visualizations
        with st.spinner("Generating visualizations..."):
            chart, heatmap = create_time_signature_visualizations(imslp_db)
            
            st.altair_chart(chart, use_container_width=True)
            st.altair_chart(heatmap, use_container_width=True)
        
        # Time signature explorer
        st.markdown("### Explorer: Compare Two Time Signatures")
        
        col1, col2 = st.columns(2)
        with col1:
            sig1 = st.selectbox("First Time Signature:", time_signatures_list, 
                                index=time_signatures_list.index('4/4') if '4/4' in time_signatures_list else 0)
        
        with col2:
            remaining_sigs = [sig for sig in time_signatures_list if sig != sig1]
            sig2 = st.selectbox("Second Time Signature:", remaining_sigs, 
                               index=remaining_sigs.index('3/4') if '3/4' in remaining_sigs else 0)
        
        # Create comparison chart
        if sig1 and sig2:
            with st.spinner("Generating comparison..."):
                comparison_chart = create_comparison_chart(imslp_db, sig1, sig2)
                st.altair_chart(comparison_chart, use_container_width=True)
            
            # Show examples of each signature
            st.markdown(f"#### Example Movements in {sig1} Time:")
            examples_1 = get_movements_by_time_signature(imslp_db, sig1)
            if examples_1:
                for ex in random.sample(examples_1, min(3, len(examples_1))):
                    st.markdown(f"- **{ex['composer']}**: {ex['work']} - {ex['movement']}")
            
            st.markdown(f"#### Example Movements in {sig2} Time:")
            examples_2 = get_movements_by_time_signature(imslp_db, sig2)
            if examples_2:
                for ex in random.sample(examples_2, min(3, len(examples_2))):
                    st.markdown(f"- **{ex['composer']}**: {ex['work']} - {ex['movement']}")

    # ===============
    # === Sidebar ===
    # ===============
    with st.sidebar:
        st.markdown("### ℹ️ About This Tool")
        st.write("""
        This tool helps you explore classical music time signatures through search, 
        random discovery, and data visualization. Listen to works while viewing time 
        signature information.
        """)
        
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
        
        for sig, count in sorted_sigs[:10]:  # Show top 10
            st.text(f"{sig}: {count} movements")
        
        if len(sorted_sigs) > 10:
            with st.expander("Show all time signatures"):
                for sig, count in sorted_sigs[10:]:
                    st.text(f"{sig}: {count} movements")
        
        # Data collection tool link
        st.markdown("### 🔧 Data Collection")
        st.markdown("""
        Want to expand the dataset? Use the 
        [music21](https://web.mit.edu/music21/) Python library 
        to extract time signatures from more classical works.
        """)

# Run the app
if __name__ == "__main__":
    main()
