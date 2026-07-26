# Installation Guide

## Requirements
- Python 3.9+
- Recommended: A virtual environment (venv, conda)
- Google Gemini API Key

## Setup

1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Install dependencies**
   Run the following command to install all required libraries:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On some systems, installing PyTorch (required by EasyOCR) or Kaleido (required for PDF chart exports) may require system-specific binary installations. Please refer to their respective official documentation if pip fails.*

3. **Initialize the application**
   Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

4. **First Run Configuration**
   - The app will automatically open in your browser (default `http://localhost:8501`).
   - Navigate to the **Settings** page in the sidebar.
   - Enter your **Google Gemini API Key**.
   - (Optional) Configure your Company Name and Theme preferences.
   - Click **Save Settings**.

You are now ready to create your first Case and upload evidence!
