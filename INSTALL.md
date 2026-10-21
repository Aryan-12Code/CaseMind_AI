# Installation Guide

## Requirements

- Python **3.10 or newer**
- A virtual environment is recommended (`venv` or conda)
- A **Groq API key** (free keys: https://console.groq.com/keys)
- Internet access (Groq API calls, and a one-time download of the EasyOCR English model on first image upload)

## Setup

1. **Get the code** and open a terminal in the project folder.

2. **Create and activate a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # macOS / Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *EasyOCR depends on PyTorch, which is a large download and may need a platform-specific build. If pip fails, follow the official PyTorch/EasyOCR instructions, then re-run the command.*

4. **(Optional) Charts inside PDF reports**
   ```bash
   pip install kaleido
   ```
   Without `kaleido` the PDF report is still generated, just without the embedded charts.

5. **Provide your Groq API key** – either:
   - set an environment variable before launching:
     ```bash
     set GROQ_API_KEY=your_api_key_here        # Windows (cmd)
     $env:GROQ_API_KEY="your_api_key_here"     # Windows (PowerShell)
     export GROQ_API_KEY=your_api_key_here     # macOS / Linux
     ```
   - or enter it later on the **Settings** page.

6. **Run the app**
   ```bash
   streamlit run app.py
   ```
   The app opens at `http://localhost:8501`.

## First Run

1. If you did not set the environment variable, open **Settings**, paste your **Groq API key**, press **Save Key**, then **Test Connection**.
2. (Optional) Set the Company / Agency name used on report cover pages, then press **Save Application Settings**.
3. Go back to the home screen, create a case and upload evidence.

The folders `database/` and `uploads/` are created automatically and contain case data; keep them out of version control (they are already in `.gitignore`).

## Troubleshooting

- **AI features disabled / "API key" message** – add a valid Groq key in Settings or via `GROQ_API_KEY`.
- **Rate limit (429) errors** – wait a moment and retry, or upgrade your Groq plan.
- **First image upload is slow** – EasyOCR is downloading and loading its model; later uploads are faster.
- **No charts in the PDF report** – install `kaleido` (step 4).
