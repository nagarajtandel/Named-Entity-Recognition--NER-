# Named Entity Recognition (NER) 

` A fully interactive **Named Entity Recognition (NER)** web application built with **Streamlit** and **spaCy**, allowing users to extract, visualize, and analyze entities from text, PDFs, or DOCX files. This app also supports **dynamic entity selection**, **session saving**, **AgGrid tables**, and **highlighted visualizations**.`

---

## 🚀 Features

- Extract entities from:
  - Plain text  
  - PDF files (supports OCR if scanned)  
  - DOCX documents  

- Select which entity types to visualize dynamically:  
  `PERSON, ORG, GPE, LOC, EVENT, DATE, NORP, PRODUCT, WORK_OF_ART, LANGUAGE, MONEY, QUANTITY, PERCENT, CARDINAL`  

- Interactive **AgGrid tables** with:
  - Searchable & sortable columns  
  - Pagination  
  - CSV & JSON export  

- **Displacy entity visualization** with custom colors  
- **Entity statistics** displayed as bar charts  
- Save sessions to revisit previous extractions  
- Success and warning messages after extraction  

---

## 📦 Installation

1. Clone the repository:

    - *git clone* <`https://github.com/nagarajtandel/Named-Entity-Recognition--NER-`>
    - *cd* <your-repo-folder>


2. Create a virtual environment:

    - python -m venv .venv
    - source .venv/bin/activate    # Linux/macOS
    - .venv\Scripts\activate       # Windows


3. Install dependencies:

    - pip install -r requirements.txt


4. Download spaCy models:

    - python -m spacy download en_core_web_sm
    # or for transformer-based model:
    - python -m spacy download en_core_web_trf

## Usage

1. Run the Streamlit app:

`streamlit run app.py`

**Steps:**

    - Upload a text, PDF, or DOCX file (or type text manually).

    - Select the entity types you want to extract from the sidebar.

    - Click Extract Entities.

`View results in tabs:`

    - Entities Table: Search, sort, and export entities

    - Visualization: Highlighted text with entity colors

    - Stats: Entity counts and charts

    - Saved Sessions: Reload previous extractions

## 🎨 Customization

    - Modify entity colors in app.py under the colors dictionary.

    - Add or remove entities from the entity_options list.

    - Switch between en_core_web_sm or en_core_web_trf for speed vs     accuracy.

## 📊 Libraries & Tools

    - Python 3.8+

    - Streamlit

    - spaCy (NER models: en_core_web_sm, en_core_web_trf)

    - PyPDF2 -- for PDF reading

    - python-docx -- for DOCX extraction

    - st-aggrid -- for interactive tables

     - Altair -- for charts

## ⚙️ File Structure

├─ app.py              # Main Streamlit application
├─ requirements.txt    # Python dependencies
├─ README.md           # Project documentation
├─ NER.ipynb           # Optional notebook for testing spaCy NER
├─ NER_Output.png      # Example output image

## 📝 Example

**Input Text:**

`Elon Musk founded Tesla in 2003. The 2024 Summer Olympics will be held in Paris, France. `  


**Entities Extracted:**

| Text                 | Label  |
|----------------------|--------|
| Elon Musk            | PERSON |
| Tesla                | ORG    |
| 2003                 | DATE   |
| 2024 Summer Olympics | EVENT  |
| Paris                | GPE    |
| France               | GPE    |

**Visualization:**

    - Highlighted text with colors for each entity type.

    - Charts showing counts of entity types.

**💡 Tips**

    - Use transformer model en_core_web_trf for better accuracy on complex text.

    - Upload large documents in PDF/DOCX format for batch extraction.

    - Use Saved Sessions to compare multiple extractions without reloading files.

**📜 License**

`MIT License © 2025`


