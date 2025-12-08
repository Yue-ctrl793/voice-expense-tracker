# Setup & Installation Guide

This guide provides instructions to set up the Voice Expense Tracker locally.

For the quickest experience, please verify the application using the live deployment link: 
https://voice-expense-tracker-efjeqy7kjlpzxawubbpswd.streamlit.app/. 
If you wish to run the code locally, follow the steps below.

## 1. Prerequisites

Ensure the following are installed on your system:

* **Python 3.9+**
* **FFmpeg**: Required for audio processing (Whisper).
    * **Mac:** `brew install ffmpeg`
    * **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/) and add to PATH, or use `choco install ffmpeg`.
    * **Linux:** `sudo apt install ffmpeg`

## 2. Installation

### Step 1: Clone the Repository

```bash
git clone [https://github.com/Yue-ctrl793/voice-expense-tracker.git](https://github.com/Yue-ctrl793/voice-expense-tracker.git)
cd voice-expense-tracker
```

### Step 2: Create a Virtual Environment (Recommended)

It is highly recommended to use a virtual environment to manage dependencies.
* **Mac/Linux:** 
```bash
python3 -m venv .venv
source .venv/bin/activate
```
* **Windows:** 
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. API Configuration (DeepSeek)

This project uses DeepSeek V3 for logic extraction and reasoning. You need a valid DeepSeek API Key to run the app locally.

Create a secrets file in the .streamlit directory:

* **Mac/Linux:** : mkdir -p .streamlit && touch .streamlit/secrets.toml

* **Windows:** : Manually create a folder named .streamlit and a file named secrets.toml inside it.

Open .streamlit/secrets.toml and add your API Key:
```bash
# .streamlit/secrets.toml
DEEPSEEK_API_KEY = "sk-72dffba7962240dab3ef69f92229d83e"
```

Note: This project points to https://api.deepseek.com. A standard OpenAI key will NOT work. 

## 4. Running the application
To start the Streamlit interface:
```bash
streamlit run src/app.py
```
The application will open in your browser at http://localhost:8501

## 5. Running Evaluation(optional)

To reproduce the evaluation metrics reported in the README:

1. Navigate to the notebooks directory:

```bash
cd notebooks
```

2. Run the evaluation notebook:

```bash
pip install jupyter
jupyter notebook evaluation.ipynb
```

3. Execute all cells to run Phase I (Synthetic Logic Test) and Phase II (End-to-End Pipeline Test).

## Troubleshooting

ModuleNotFoundError: No module named 'whisper': Ensure you activated the virtual environment before running the app.

FileNotFoundError: ffmpeg: Verify that FFmpeg is installed and added to your system PATH.
