# CaseMind AI

**CaseMind AI** is a professional, intelligent digital evidence investigation platform designed to streamline the analysis of unstructured data. It combines traditional file parsing (OCR, PDF extraction) with advanced Natural Language Processing (NLP) and Google Gemini AI to uncover relationships, identify high-risk individuals, and summarize complex cases automatically.

## Features

- **Case Management**: Complete isolation between investigations. Each case gets its own SQLite database and uploads directory.
- **Automated Evidence Extraction**: Drag-and-drop support for PDFs, TXT, CSV, EML, and Images. Auto-extracts text, metadata, and entities.
- **AI Investigation Engine**: Powered by Google Gemini to provide a chat interface constrained *strictly* to uploaded evidence. Automatically generates comprehensive Case Summaries.
- **Investigation Analytics**: Live tracking of entities, keyword frequencies, and dynamic interactive charts using Plotly.
- **Suspicion Score Leaderboard**: Rule-based scoring engine to flag high-risk individuals based on their association with sensitive keywords (e.g., money, passwords, destruction of evidence).
- **Interactive Relationship Graph**: NetworkX and PyVis powered graph to map out connections between People, Organizations, and Locations.
- **Professional Reporting**: Export comprehensive multi-page PDF reports (with embedded charts), Excel workbooks, CSVs, and JSON data dumps.

## Getting Started

Please see `INSTALL.md` for full installation instructions, and `USER_GUIDE.md` for instructions on how to use the application.

## Tech Stack
- **Frontend**: Streamlit, Plotly, PyVis
- **Backend**: Python 3.10+, SQLite3
- **AI / OCR**: Google GenAI SDK, EasyOCR, spaCy, pdfplumber
- **Export**: fpdf2, openpyxl, kaleido
