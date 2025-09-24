import streamlit as st
import spacy
import pandas as pd
from spacy import displacy
from collections import Counter
import altair as alt
import json

# File handling libraries
from PyPDF2 import PdfReader
import docx

# AgGrid
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

# ---------------------------
# Helpers: text extraction
# ---------------------------
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
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
# Setup UI + session
# ---------------------------
st.set_page_config(page_title="Dynamic NER App", layout="wide")
st.title("🌟 Dynamic Named Entity Recognition (NER) — Pro")

if "saved_sessions" not in st.session_state:
    st.session_state.saved_sessions = []

# Sidebar controls
st.sidebar.header("Settings / Uploads")

model_choice = st.sidebar.selectbox("spaCy model", ["en_core_web_sm", "en_core_web_trf"])
uploaded_file = st.sidebar.file_uploader("Upload file (TXT, PDF, DOCX)", type=["txt","pdf","docx"])
select_all_button = st.sidebar.button("Select All Entities")

# Entity colors
colors = {
    'PERSON': 'linear-gradient(90deg, #7ee7f2, #0f62fe)',
    'ORG': 'linear-gradient(90deg, #f28c8c, #e63946)',
    'GPE': 'linear-gradient(90deg, #90be6d, #43aa8b)',
    'LOC': 'linear-gradient(90deg, #f9c74f, #f9844a)',
    'EVENT': 'linear-gradient(90deg, #f2c707, #dc9ce7)',
    'DATE': 'linear-gradient(90deg,#aa9cde,#dc9ce7)',
    'NORP': 'linear-gradient(90deg,#f8961e,#f3722c)',
    'PRODUCT': 'linear-gradient(90deg,#577590,#4d908e)',
    'WORK_OF_ART': 'linear-gradient(90deg,#9d4edd,#c77dff)',
    'LANGUAGE': 'linear-gradient(90deg,#43aa8b,#90be6d)',
    'MONEY': 'linear-gradient(90deg,#f94144,#f3722c)',
    'QUANTITY': 'linear-gradient(90deg,#f8961e,#f9c74f)',
    'PERCENT': 'linear-gradient(90deg,#90be6d,#43aa8b)',
    'CARDINAL': 'linear-gradient(90deg,#577590,#4d908e)'
}

entity_options = list(colors.keys())

# ---------------------------
# Load spaCy model safely
# ---------------------------
@st.cache_resource(show_spinner=False)
def load_model(name):
    try:
        return spacy.load(name)
    except Exception as e:
        return None

nlp = load_model(model_choice)
if nlp is None:
    st.sidebar.error(f"Model {model_choice} not found. Install with `python -m spacy download {model_choice}`.")
    st.stop()

# ---------------------------
# Main layout: tabs
# ---------------------------
tabs = st.tabs(["Input", "Entities Table", "Visualization", "Stats", "Saved Sessions"])

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

# ---------------------------
# Extraction and display
# ---------------------------
# ---------------------------
# Extraction and display
# ---------------------------
if extract_button and text:
    with st.spinner("Extracting entities..."):
        doc = nlp(text)

        # filter entities by selected_ents
        filtered_ents = [ent for ent in doc.ents if ent.label_ in st.session_state.selected_ents]

        df = pd.DataFrame(
            [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in filtered_ents],
            columns=["Text", "Start", "End", "Label"]
        )

        # Save session snapshot
        session_snapshot = {
            "text": text,
            "entities": df.to_dict(orient="records"),
            "selected_ents": st.session_state.selected_ents,
            "model": model_choice
        }
        st.session_state.saved_sessions.append(session_snapshot)

    # ✅ Success or warning message
    if filtered_ents:
        st.success("✅ Extraction completed successfully!")
    else:
        st.warning("⚠️ No entities found for the selected types.")


    # ---------------------------
    # Entities Table (AgGrid)
    # ---------------------------
    with tabs[1]:
        st.header("Entities Table (Searchable / Sortable)")
        if df.empty:
            st.info("No entities detected for the selected types.")
        else:
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
            gb.configure_side_bar()
            gb.configure_default_column(filterable=True, sortable=True, resizable=True)
            gb.configure_selection(selection_mode="single", use_checkbox=True)
            gridOptions = gb.build()

            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.NO_UPDATE,
                enable_enterprise_modules=False,
                fit_columns_on_grid_load=True
            )

            df_filtered = pd.DataFrame(grid_response["data"])

            if not df_filtered.empty:
                csv = df_filtered.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV (current view)", csv, "entities_view.csv", "text/csv")
                st.download_button(
                    "Download JSON (current view)",
                    json.dumps(df_filtered.to_dict(orient="records")),
                    "entities_view.json",
                    "application/json"
                )

    # ---------------------------
    # Visualization
    # ---------------------------
    with tabs[2]:
        st.header("Entity Visualization")
        options_displacy = {
            "ents": st.session_state.selected_ents,
            "colors": {k: v for k, v in colors.items() if k in st.session_state.selected_ents}
        }
        html = displacy.render(doc, style="ent", options=options_displacy, jupyter=False)
        height = max(300, len(filtered_ents) * 50)
        st.components.v1.html(html, height=height, scrolling=True)
        st.download_button("Download highlighted HTML", html, "highlighted_entities.html", "text/html")

    # ---------------------------
    # Stats
    # ---------------------------
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

# ---------------------------
# Saved sessions tab
# ---------------------------
with tabs[4]:
    st.header("Saved Sessions (this run)")
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
        st.write("No saved sessions yet. Click 'Extract Entities' to create snapshots.")
