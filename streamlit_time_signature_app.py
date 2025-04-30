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

# === Matching Function ===
def match_imslp_title(query, imslp_db):
    best_match = None
    best_score = 0
    matched_composer = None

    for composer, works in imslp_db.items():
        for work_title in works:
            ratio = difflib.SequenceMatcher(None, query.lower(), work_title.lower()).ratio()
            if ratio > best_score and ratio > 0.5:
                best_match = work_title
                matched_composer = composer
                best_score = ratio

    if matched_composer and best_match:
        return matched_composer, best_match, imslp_db[matched_composer][best_match]
    return None, None, None

# === Streamlit UI ===
st.set_page_config(page_title="Classical Time Signature Lookup", layout="centered")
st.title("🎵 Classical Time Signature Lookup")
st.markdown("""
Type a classical work name (e.g., **Mozart Symphony 24**, **Beethoven Sonata Moonlight**) and see its time signatures for each movement.
""")

query = st.text_input("Enter Work Title:", "Mozart Symphony 24")

if query:
    imslp_db = load_imslp_database()
    composer, work, result = match_imslp_title(query, imslp_db)

    if composer and work:
        st.success(f"Matched Work: {work}\nby {composer}")
        for mv in result:
            st.markdown(f"- **{mv['movement']}** — `{mv['time_signature']}`")
    else:
        st.warning("No match found in dataset.")

# === Optional: Show Dataset ===
with st.expander("📂 View Raw Dataset (Sample)"):
    st.json({k: list(v.keys())[:2] for k, v in imslp_db.items()})
