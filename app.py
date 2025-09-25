import streamlit as st
import spacy
import pandas as pd
from spacy import displacy
from collections import Counter
import altair as alt
import json
import subprocess
from PyPDF2 import PdfReader
import docx

# ---------------------------
# Helpers: text extraction
# ---------------------------
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text)
    except Exception as e:
        return f"[PDF extraction error] {e}"

def extract_text_from_docx(uploaded_file):
    try:
        doc = docx.Document(uploaded_file)
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[DOCX extraction error] {e}"

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title="Dynamic NER App", layout="wide")
st.title("🌟 Dynamic Named Entity Recognition (NER) — Pro")

if "saved_sessions" not in st.session_state:
    st.session_state.saved_sessions = []

# Sidebar
st.sidebar.header("Settings / Uploads")
model_choice = st.sidebar.selectbox("spaCy model", ["en_core_web_sm", "en_core_web_trf"])
uploaded_file = st.sidebar.file_uploader("Upload file (TXT, PDF, DOCX)", type=["txt","pdf","docx"])
select_all_button = st.sidebar.button("Select All Entities")

# ---------------------------
# Load SpaCy model
@st.cache_resource(show_spinner=False)
def load_model(name):
    try:
        return spacy.load(name)
    except OSError:
        with st.spinner(f"Downloading {name} model..."):
            subprocess.run(["python", "-m", "spacy", "download", name])
        return spacy.load(name)

nlp = load_model(model_choice)

# ---------------------------
# Entity colors
colors = {
    'PERSON':'#7ee7f2', 'ORG':'#f28c8c', 'GPE':'#90be6d', 'LOC':'#f9c74f',
    'EVENT':'#f2c707', 'DATE':'#aa9cde', 'NORP':'#f8961e', 'PRODUCT':'#577590',
    'WORK_OF_ART':'#9d4edd', 'LANGUAGE':'#43aa8b', 'MONEY':'#f94144',
    'QUANTITY':'#f8961e', 'PERCENT':'#90be6d', 'CARDINAL':'#577590'
}
entity_options = list(colors.keys())

# ---------------------------
# Tabs
tabs = st.tabs(["Input", "Entities Table", "Visualization", "Stats", "Saved Sessions"])

# ---------- Input tab ----------
with tabs[0]:
    st.header("Input Text")
    if uploaded_file:
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext == "pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif ext == "docx":
            text = extract_text_from_docx(uploaded_file)
        else:
            text = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Uploaded Text (preview)", value=text, height=240)
    else:
        text = st.text_area("Enter text manually", height=240)

    if "selected_ents" not in st.session_state:
        st.session_state.selected_ents = entity_options.copy()

    selected_ents = st.multiselect(
        "Select entity types to visualize",
        options=entity_options,
        default=st.session_state.selected_ents
    )
    st.session_state.selected_ents = selected_ents

    extract_button = st.button("Extract Entities")

    if select_all_button:
        st.session_state.selected_ents = entity_options.copy()
        st.experimental_rerun()

# ---------- Extraction ----------
if extract_button and text:
    with st.spinner("Extracting entities..."):
        doc = nlp(text)
        filtered_ents = [ent for ent in doc.ents if ent.label_ in st.session_state.selected_ents]

        df = pd.DataFrame(
            [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in filtered_ents],
            columns=["Text", "Start", "End", "Label"]
        )

        # Save session
        session_snapshot = {
            "text": text,
            "entities": df.to_dict(orient="records"),
            "selected_ents": st.session_state.selected_ents,
            "model": model_choice
        }
        st.session_state.saved_sessions.append(session_snapshot)

    if filtered_ents:
        st.success("✅ Extraction completed successfully!")
    else:
        st.warning("⚠️ No entities found for the selected types.")

    # ---------- Entities Table ----------
    with tabs[1]:
        st.header("Entities Table")
        if df.empty:
            st.info("No entities detected for the selected types.")
        else:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "entities_view.csv", "text/csv")
            st.download_button("Download JSON", json.dumps(df.to_dict(orient="records")), "entities_view.json", "application/json")

    # ---------- Visualization ----------
    with tabs[2]:
        st.header("Entity Visualization")
        options_displacy = {
            "ents": st.session_state.selected_ents,
            "colors": {k: v for k,v in colors.items() if k in st.session_state.selected_ents}
        }
        html = displacy.render(doc, style="ent", options=options_displacy, jupyter=False)
        height = max(300, len(filtered_ents) * 50)
        st.components.v1.html(html, height=height, scrolling=True)
        st.download_button("Download highlighted HTML", html, "highlighted_entities.html", "text/html")

    # ---------- Stats ----------
    with tabs[3]:
        st.header("Entity Statistics")
        if filtered_ents:
            entity_counts = Counter([ent.label_ for ent in filtered_ents])
            df_counts = pd.DataFrame(entity_counts.items(), columns=["Entity Type", "Count"])
            chart = alt.Chart(df_counts).mark_bar().encode(
                x="Entity Type",
                y="Count",
                color="Entity Type"
            ).properties(width=700)
            st.altair_chart(chart)
            st.table(df_counts.sort_values("Count", ascending=False).reset_index(drop=True))
        else:
            st.write("No entities to display statistics for.")

# ---------- Saved Sessions ----------
with tabs[4]:
    st.header("Saved Sessions")
    if st.session_state.saved_sessions:
        for i, snap in enumerate(st.session_state.saved_sessions[::-1], 1):
            st.subheader(f"Session #{i}")
            st.write("Model:", snap.get("model"))
            st.write("Selected entity types:", snap.get("selected_ents"))
            st.write("Entities count:", len(snap.get("entities", [])))
            if st.button(f"Load session #{i}", key=f"load_{i}"):
                st.session_state.selected_ents = snap.get("selected_ents", entity_options)
                st.text_area("Loaded session text (read-only)", value=snap.get("text",""), height=200)
    else:
        st.write("No saved sessions yet.")
