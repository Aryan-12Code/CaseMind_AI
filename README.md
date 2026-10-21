# CaseMind AI

**CaseMind AI** is an AI-assisted digital evidence investigation platform built with Streamlit. Investigators create a case, upload mixed-format evidence (PDF, images, TXT, CSV, EML), and CaseMind AI extracts the text, identifies the people, organizations, locations, dates and money involved, builds a timeline and suspicion scores, and lets them ask questions that are answered **only from the uploaded evidence**, with the source file cited.

## Features

- **Case management** – Every investigation is isolated. A master `cases.db` tracks cases (name, status); each case gets its own SQLite database (`database/cases/<id>/evidence.db`) and its own upload folders.
- **Multi-format evidence ingestion** – Drag-and-drop upload of PDF, PNG, JPG, TXT, CSV and EML files with automatic text extraction and metadata capture.
- **LLM-based entity extraction** – Groq-hosted Llama 3.3 70B (JSON mode, temperature 0) identifies persons, organizations, locations, dates and money. Names are cleaned and name variants (e.g. "Rahul" and "Rahul Sharma") are merged.
- **Keyword analytics** – Regex-based extraction of email addresses, phone numbers, dates, currency values, URLs and numbers.
- **Evidence-grounded AI chat** – Questions are answered strictly from the case evidence; every answer lists its source file(s) and a supporting excerpt. Conversations are saved per case.
- **AI case summary and insights** – One-click investigation summary (findings, people, organizations, locations, dates, transactions, observations, suggested questions) and automatic insights (most-mentioned person, key date/location/keyword, suspicious activity).
- **Investigation timeline** – Chronological events built from the dates found in the evidence.
- **Suspicion score leaderboard** – Transparent, rule-based scoring (e.g. money mentions, password/credential mentions, destruction-of-evidence terms, confidentiality markers, urgency, appearing in multiple files), capped at 100.
- **Entity profile cards** – Per-person dossiers showing connected people, locations, documents and money, built from the extracted entities.
- **Global search** – Full-text search across all processed evidence with highlighted snippets.
- **Reports and exports** – Multi-page PDF report (cover page, executive summary, suspicion scores, optional charts), Excel workbook, CSV and JSON.

## Tech Stack

| Layer | Technology |
|---|---|
| Interface | Streamlit, streamlit-option-menu, Plotly |
| Language / storage | Python 3.10+, SQLite3, pandas, python-dateutil |
| AI | Groq API (`llama-3.3-70b-versatile`) via the `groq` Python SDK |
| Extraction | pdfplumber (PDF), EasyOCR (images), pandas (CSV), Python `email` module (EML) |
| Export | fpdf2 (PDF), openpyxl (Excel); `kaleido` optional for charts inside the PDF |

## Quick Start

```bash
pip install -r requirements.txt
set GROQ_API_KEY=your_api_key_here      # Windows (use `export` on macOS/Linux)
streamlit run app.py
```

You can also paste the key into the **Settings** page after launch. See [INSTALL.md](INSTALL.md) for details and [USER_GUIDE.md](USER_GUIDE.md) for how to use the app.

## Project Structure

```
CaseMindAI/
├── app.py                  # Streamlit entry point, sidebar navigation and routing
├── requirements.txt
├── .streamlit/config.toml  # Dark theme
└── modules/
    ├── *_view.py           # One file per page (home, dashboard, upload, analytics, ...)
    ├── cases_db.py         # Master case registry (cases.db)
    ├── database.py         # Per-case SQLite storage (evidence, processed text, chat history)
    ├── text_extractor.py   # Routes each file type to its processor
    ├── pdf_processor.py / image_processor.py / csv_processor.py / email_processor.py
    ├── entity_extractor.py / entity_normalizer.py   # Groq LLM NER + cleaning/merging
    ├── keyword_extractor.py, timeline_generator.py, suspicion_score.py, relationship_builder.py
    ├── ai_engine.py, chat_manager.py, citation_engine.py, summary_generator.py, insight_generator.py
    └── export_manager.py, dashboard_export.py, chart_generator.py, search_engine.py, ...
```

## Known Limitations

- Image-only (scanned) PDFs are not OCR'd; only digital PDFs yield text. Image files (PNG/JPG) are OCR'd with EasyOCR.
- Entity extraction reads at most the first 20,000 characters of each file.
- AI features need a Groq API key and an internet connection. Evidence text is sent to Groq during entity extraction, chat and summary generation.
- Suspicion scores are keyword/rule based and are an aid for prioritising review, not evidence of wrongdoing.
