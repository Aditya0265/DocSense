# 📄 PDF Extractor Pro


![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Active-success)


------------------------------------------------------------------------

## 📌 Overview

**PDF Extractor Pro** is an enhanced document intelligence tool designed
to extract structured content from PDF files and perform persona-driven
semantic document analysis.

The system combines classical PDF parsing, document structure detection,
and lightweight machine learning-based semantic ranking to help users
quickly identify relevant sections of documents based on user roles and
job tasks.

This project demonstrates practical implementation of:
- PDF text and image extraction
- Document hierarchy detection
- Semantic document ranking
- Readability & text complexity analysis
- PII detection and PDF redaction
- Interactive Streamlit-based user interface

------------------------------------------------------------------------

## 🧠 System Workflow

```
PDF Upload
   ↓
Text + Image Extraction
   ↓
Document Structure Detection
   ↓
Readability Scoring & Text Analytics
   ↓
Persona + Task Mapping
   ↓
Semantic Ranking (TF-IDF + Cosine Similarity)
   ↓
Redaction / Export / Structured Results
```

------------------------------------------------------------------------

## 🚀 Key Features

### 📑 Advanced PDF Extraction

-   Extract full text from PDFs
-   Extract embedded images
-   Handles multi-page documents
-   OCR support for scanned PDFs (if Tesseract is installed)

------------------------------------------------------------------------

### 🧠 Document Structure Intelligence

-   Title detection
-   Heading detection (H1–H3 approximation)
-   Font-based clustering using KMeans
-   Converts raw PDFs into structured document representation

------------------------------------------------------------------------

### 👤 Persona-Based Document Intelligence

-   Persona-driven semantic search
-   TF-IDF document vectorization
-   Cosine similarity-based section ranking
-   Persona + Task → Relevant Document Sections mapping
-   JSON-style structured outputs

------------------------------------------------------------------------

### 🌍 Multilingual Support

-   Google Translator wrapper support
-   Helps analyze documents in multiple languages

------------------------------------------------------------------------

### 📊 Text Analytics

-   Word Cloud generation
-   Basic data visualization using Matplotlib
-   Quick document theme understanding

------------------------------------------------------------------------

### 📖 Readability Analysis

-   **Flesch Reading Ease** — overall readability score (0–100)
-   **Flesch-Kincaid Grade Level** — U.S. school grade equivalent
-   **Gunning Fog Index** — years of education needed to understand
-   **Coleman-Liau Index** — character-based grade level estimate
-   Estimated reading time (based on 200 WPM)
-   Word count, sentence count, and average sentence length
-   Complexity breakdown with visual bar (simple vs complex words)
-   Human-friendly reading level labels (e.g., "Standard (8th–9th Grade)")

------------------------------------------------------------------------

### 🛡️ PDF Redaction Tool

-   Redact sensitive information by drawing black rectangles over matched text
-   **Custom keywords** — enter any words or phrases to black out
-   **5 built-in PII patterns:**
    -   Email addresses
    -   Phone numbers
    -   Dates (DD/MM/YYYY)
    -   URLs
    -   Currency amounts ($, £, €, ₹)
-   **Custom regex** — supply your own pattern for advanced redaction
-   Per-page redaction count with bar chart visualization
-   Download the redacted PDF directly from the app

------------------------------------------------------------------------

### 📦 Export & Output Management

-   Structured output folders
-   Extracted images ZIP download
-   Extracted text export
-   Excel export for extracted tables
-   Redacted PDF download
-   Temporary file cleanup

------------------------------------------------------------------------

### 💻 Professional Web Interface

-   Built using Streamlit
-   Custom CSS dark theme
-   10-tab dashboard: Metadata · Structure · Reader · Tables · Visuals · Readability · Gallery · Export · Redact · Persona AI
-   Clean upload → analyze → download workflow

------------------------------------------------------------------------

## 🛠 Tech Stack

### Core

-   Python 3.x
-   Streamlit

### PDF Processing

-   PyMuPDF (fitz)
-   pdfplumber

### Machine Learning

-   Scikit-learn
    -   TF-IDF Vectorizer
    -   Cosine Similarity
    -   KMeans Clustering

### NLP & Processing

-   WordCloud
-   Regex
-   Unicode normalization

### Text Analytics

-   Flesch Reading Ease / Flesch-Kincaid (custom implementation)
-   Gunning Fog Index (custom implementation)
-   Coleman-Liau Index (custom implementation)

### OCR (Optional)

-   Tesseract OCR
-   pytesseract

### Data & Visualization

-   Pandas
-   NumPy
-   Matplotlib
-   Pillow

------------------------------------------------------------------------

## 📂 Project Structure

```
PDF-Extractor-Pro/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker containerization
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── extractor.py        # PDF text, image, table extraction + OCR
│   ├── persona_intel.py    # Persona-based semantic ranking (TF-IDF)
│   ├── readability.py      # Readability scoring & text metrics
│   ├── redactor.py         # PII detection & PDF redaction
│   └── utils.py            # File handling, validation, cleanup
│
├── downloads/              # Output directory (generated at runtime)
└── temp_uploads/           # Temporary upload storage (auto-cleaned)
```

------------------------------------------------------------------------

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Aditya0265/PDF-Extractor-Pro.git
cd PDF-Extractor-Pro
```

------------------------------------------------------------------------

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Mac / Linux:

```bash
source venv/bin/activate
```

------------------------------------------------------------------------

### 3️⃣ Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Run Application

```bash
python -m streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

------------------------------------------------------------------------

## 🧪 Example Use Cases

-   Research paper analysis
-   Policy document review
-   Business document filtering
-   Academic document intelligence demos
-   Readability assessment of reports and publications
-   Redacting PII before sharing documents externally
-   Hackathon and portfolio demonstration

------------------------------------------------------------------------

## ⚠️ Limitations

-   Uses TF-IDF (not deep LLM semantic reasoning)
-   OCR accuracy depends on scan quality
-   Structure detection is heuristic-based
-   Very large PDFs may increase processing time
-   Currently optimized for **English-language PDFs only**
-   Non-English documents may produce inaccurate structure detection or semantic ranking
-   Readability formulas are designed for English text
-   Redaction works on text-based PDFs; scanned/image-only PDFs require OCR first

------------------------------------------------------------------------

## 📌 Future Improvements

-   Vector database (FAISS) integration
-   LLM reasoning layer
-   Multi-document semantic search
-   Auto summarization
-   Cloud deployment support
-   Batch redaction across multiple PDFs
-   Named Entity Recognition (NER) for smarter PII detection

------------------------------------------------------------------------
