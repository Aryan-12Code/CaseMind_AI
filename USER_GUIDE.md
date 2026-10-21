# User Guide – CaseMind AI

## Core Workflow

### 1. Case management (Home)
- **Create a case:** enter a case name and create it.
- **Open a case:** press **Open Case** on any investigation in the list.
- **Manage cases:** rename a case, set its status (In Progress, Completed, Archived) or delete it. Deleting a case removes it from the case list; its files under `database/` and `uploads/` are not erased by the app, so delete them manually if the data must be destroyed.
- Use **Close Case** in the sidebar to return to the case list.

### 2. Upload evidence
Open **Upload Evidence** inside a case.
- Drag and drop files. Supported formats: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.csv`, `.eml`.
- Each file is saved in the case, its text is extracted (pdfplumber for PDFs, EasyOCR for images, pandas for CSV, the email parser for EML), keywords are extracted, and the Groq model identifies people, organizations, locations, dates and money.
- Wait for the success checks before leaving the page. Scanned (image-only) PDFs produce no text; upload them as images instead.
- Below the uploader, the **Evidence Manager** lets you search, filter, preview, open details for, or delete files, and a **global search** finds text across all evidence.

### 3. Review entities, keywords and analytics
- **Dashboard** – live evidence, entity and storage metrics.
- **Entity Explorer** – browse people, organizations, locations, dates and money found in the files.
- **Keyword Analytics** – emails, phone numbers, dates, currency values, URLs and numbers.
- **Analytics** – interactive charts and the **Suspicion Score Leaderboard** with the reasons behind each score.
- **Relationship Graph** – entity profile cards: for each person, connected people, locations, documents and money.
- **Timeline** – chronological events built from dates in the evidence; sort ascending or descending.

### 4. AI analysis
- On the **Dashboard**, press **Analyze Evidence** for a full case summary (findings, entities, observations, suggested questions) and **Generate AI Insights** for the key person, date, location, keyword and suspicious activity.
- Open **AI Chat**, type a question and press **Ask**. Answers use only the uploaded evidence and show the source file and a supporting excerpt. If the evidence does not contain the answer, the AI says so. Past conversations are saved with the case.

### 5. Reports and exports
Open **Investigation Reports** and use:
- **Generate Professional PDF** – cover page (with your company name), summary, suspicion scores and, if `kaleido` is installed, charts.
- **Generate Excel Export**, **Generate CSV**, **Generate JSON** – raw case data.

## Settings
Enter the Groq API key and press **Save Key**, use **Test Connection** to verify it, and set the company name, theme and default export format (**Save Application Settings**).

## Troubleshooting
- **AI features disabled:** save a valid **Groq API key** in **Settings** (or set `GROQ_API_KEY` before starting the app).
- **Rate limit message:** wait a moment and try again.
- **A file shows "Failed":** check that it is a supported, uncorrupted file; encrypted PDFs cannot be read.
- **PDF report has no charts:** install `kaleido` (`pip install kaleido`); the text content is unaffected.
- **No entities found:** check that the file produced text (scanned PDFs do not) and that your API key is valid.

## Privacy note
Evidence and results are stored locally in the case's SQLite database and `uploads/` folder. Text from your evidence is sent to the Groq API when entities are extracted and when you use AI chat, summaries or insights.
