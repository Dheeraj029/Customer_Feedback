

# 🤖 Customer Feedback Triage System

An AI-powered dashboard that classifies customer feedback, assigns urgency, and suggests next actions. It runs **Azure OpenAI** alongside a **Rule-Based Baseline** to compare performance.

## ✨ Features
*   **Dual Classification**: Compare AI (GPT-4) decisions vs. Keyword Rules.
*   **Interactive UI**: Built with Streamlit for easy file uploads and visualization.
*   **Data Export**: Download full analysis reports as JSON.

## 🛠️ Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
    AZURE_OPENAI_API_KEY=your_api_key
    AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
    AZURE_OPENAI_API_VERSION=2024-02-15-preview

## 🚀 Usage

Run the application:
```bash
streamlit run src/main.py
```

1.  Upload a `.txt` or `.csv` file containing customer feedback.
2.  Click **🚀 Start Analysis**.
3.  View side-by-side comparisons and download the JSON report.

## 📂 Project Structure
```text
├── src/
│   ├── main.py       # Core application logic
│   └── prompts.py    # System prompts
├── .env              # API credentials (gitignored)
├── requirements.txt  # Python libraries
└── README.md         # Documentation
```
