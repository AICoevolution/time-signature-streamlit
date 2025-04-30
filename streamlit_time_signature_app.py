import streamlit as st
import difflib
import json

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

            if score > 1:  # Higher score threshold
                suggestions.append((composer, work_title, works[work_title], score))

    # Sort by score
    suggestions = sorted(suggestions, key=lambda x: x[3], reverse=True)
    return suggestions[:max_results]

# === Streamlit UI ===
st.set_page_config(page_title="Classical Time Signature Lookup", layout="wide")
st.title("\ud83c\udfb5 Classical Time Signature Lookup")
st.markdown("""
Type a classical work name (e.g., **Mozart Symphony 24**, **Beethoven Sonata Moonlight**) and see time signatures for each movement.
""")

query = st.text_input("Enter Work Title:", "Mozart Symphony 24")

if query:
    imslp_db = load_imslp_database()
    results = suggest_imslp_titles(query, imslp_db)

    with st.sidebar:
        st.markdown("### Matching Works")
        if results:
            for composer, work, movements, _ in results:
                mv_list = "<br>".join([f"{mv['movement']} — {mv['time_signature']}" for mv in movements])
                html = f"""
                    <div style='font-size: 12px; margin-bottom: 1em;'>
                        <strong>{work}</strong><br><em>{composer}</em><br>{mv_list}
                    </div>
                """
                st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("No matches found.")

# === Optional: Show Dataset ===
with st.expander("\ud83d\udcc2 View Raw Dataset (Sample)"):
    st.json({k: list(v.keys())[:2] for k, v in imslp_db.items()})
