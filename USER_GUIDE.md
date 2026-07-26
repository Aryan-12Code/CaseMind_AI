# User Guide - CaseMind AI

## Core Workflow

### 1. Case Management (Home)
When you launch the app, you will see the **Home Dashboard**.
- **Create a Case**: Enter a Case Name and click "Create Case".
- **Open a Case**: Click the primary "Open Case" button on any recent investigation.
- **Manage Cases**: Use the popovers to Rename, change Status (In Progress, Completed, Archived), or completely Delete a case.

### 2. Uploading Evidence
Once a case is open, use the **Upload Evidence** tab.
- Drag and drop your files.
- Supported formats: `.pdf`, `.png`, `.jpg`, `.txt`, `.csv`, `.eml`.
- The system automatically extracts text. If you upload an image, EasyOCR is used. If you upload a PDF, text is scraped. Wait for the green success checks before leaving the page.

### 3. Reviewing Analytics & Entities
- Navigate to **Dashboard** to see live metrics.
- Navigate to **Entity Explorer** to browse a structured list of People, Organizations, and Locations found in your files.
- Navigate to **Keyword Analytics** to search for specific extracted emails, phone numbers, money values, or URLs.
- Navigate to **Analytics** to view dynamic charts and the **Suspicion Score Leaderboard**.

### 4. AI Analysis
- Navigate to the **Dashboard** and click **Analyze Evidence**. The AI will generate a massive multi-section report including Findings, Timelines, and Observations.
- Navigate to **AI Chat** to ask direct questions. The AI is sandboxed and will *only* answer using the uploaded case files. Every response includes a source citation.

### 5. Exporting Data
- Navigate to **Investigation Reports**.
- You can generate a multi-page **Professional PDF Report** that includes your company name, the AI summary, suspicion scores, and charts.
- You can also export raw data to **Excel**, **CSV**, or **JSON**.

## Troubleshooting
- **Missing API Key**: If the AI features are disabled, ensure you've saved a valid Gemini API key in the **Settings** tab.
- **PDF Charts not rendering**: The PDF export relies on `kaleido`. If it fails, the PDF will generate without the charts but text will remain intact.
