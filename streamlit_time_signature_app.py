import streamlit as st
import difflib
import json
import urllib.parse

# === Load IMSLP JSON Database ===
def load_imslp_database(path='imslp_scores_corrected.json'):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load IMSLP data: {e}")
        return {}

# === Suggestive Matching Function ===
def suggest_imslp_titles(query, imslp_db, max_results=10):
    suggestions = []

    query_words = set(query.lower().split())

    for composer, works in imslp_db.items():
        for work_title in works:
            full_text = f"{composer} {work_title}".lower()
            word_matches = sum(1 for word in query_words if word in full_text)
            ratio = difflib.SequenceMatcher(None, query.lower(), full_text).ratio()
            score = word_matches + ratio

            if score > 1:
                suggestions.append((composer, work_title, works[work_title], score))

    suggestions = sorted(suggestions, key=lambda x: x[3], reverse=True)
    return suggestions[:max_results]

# === Streamlit UI ===
st.set_page_config(page_title="Classical Time Signature Lookup", layout="wide")
st.title("🎵 Classical Time Signature Lookup")
st.markdown("""
Type a classical work name (e.g., **Mozart Symphony 24**, **Beethoven Sonata Moonlight**) and see time signatures for each movement.
""")

query = st.text_input("Enter Work Title:", "Mozart Symphony 24")

if query:
    imslp_db = load_imslp_database()
    results = suggest_imslp_titles(query, imslp_db)

    if results:
        for composer, work, movements, _ in results:
            st.markdown("---")
            st.markdown(f"### 🎼 {work}")
            st.markdown(f"*by {composer}*")

            for mv in movements:
                st.markdown(f"- **{mv['movement']}** — `{mv['time_signature']}`")

            query_encoded = urllib.parse.quote(f"{work} {composer}")
            spotify_url = f"https://open.spotify.com/search/{query_encoded}"
            imslp_url = f"https://imslp.org/index.php?search={query_encoded}&title=Special:Search&go=Go"
            youtube_url = f"https://www.youtube.com/results?search_query={query_encoded}"

            st.markdown(
                f"[🎧 Listen on Spotify]({spotify_url}) | [📜 View Score on IMSLP]({imslp_url}) | [▶️ YouTube Search]({youtube_url})",
                unsafe_allow_html=True
            )
    else:
        st.warning("No matches found.")

# === Sidebar ===
with st.sidebar:
    st.markdown("### ℹ️ About This Tool")
    st.write("Search classical works and get movement time signatures, plus links to listen or read the score.")

# === Optional: Show Dataset ===
with st.expander("📂 View Raw Dataset (Sample)"):
    st.json({k: list(v.keys())[:2] for k, v in imslp_db.items()})
