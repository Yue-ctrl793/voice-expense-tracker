# AI Voice Expense Tracker: Voice-to-Data Pipeline

Short Description: A robust, multimodal application that transcribes user voice recordings of expenses using the local Whisper model and uses the DeepSeek LLM for structured data extraction and categorization.

---

## What it Does

This application functions as an intelligent voice-activated bookkeeping system. The user uploads an audio file (e.g., "Lunch was twenty-five dollars"). The system processes this audio using a two-stage pipeline: first, the local Whisper model converts the speech to text, and second, the DeepSeek Large Language Model (LLM) extracts the item, precise amount, and assigned category into a machine-readable JSON format. Users can review and edit the extracted data before committing it to a persistent session history, where it is visualized by category and filtered by time.

---

## Quick Start

This project requires Python 3.10+ and a stable internet connection for the DeepSeek API calls.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Yue-ctr1793/voice-expense-tracker.git](https://github.com/Yue-ctr1793/voice-expense-tracker.git)
    cd voice-expense-tracker
    ```

2.  **Setup Environment and Dependencies:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
    *(Note: The first run will automatically download the Whisper 'small' model.)*

3.  **Setup API Keys and System Binaries:**
    * Ensure the system dependency **`ffmpeg`** is installed (handled via `packages.txt` on cloud deployment, may require `brew install ffmpeg` on macOS).
    * Create a file named **`.streamlit/secrets.toml`** in the root directory and add your DeepSeek API key:
        ```toml
        DEEPSEEK_API_KEY = "sk-XXXXXXXXXXXXXXXX"
        ```

4.  **Run the Application:**
    ```bash
    streamlit run src/app.py
    ```
    The application will open in your web browser.

---

## Video Links

*(请在录制完视频后，将链接粘贴到这里。)*

* **Project Demo (3-5 min):** [Link to YouTube/Vimeo Demo Video]
* **Technical Walkthrough (5-10 min):** [Link to YouTube/Vimeo Technical Walkthrough Video]

---

## Evaluation (Final Analysis)

### A. Quantitative Analysis (Model Performance)

The system was evaluated on a custom benchmark of 20 distinct audio test cases, designed to stress the pipeline under various conditions (noise, complex numbers, multi-item extraction).

| Metric | Result | Description | Rubric Point |
| :--- | :--- | :--- | :--- |
| **Average Slot Accuracy** | **71.11%** | The percentage of individual fields (Item, Amount, Category) correctly extracted. **This is the core performance metric.** | System Performance |
| **Final JSON Accuracy** | **50.00%** | The percentage of cases where the LLM output matched the ground truth perfectly (100% field match). | Strict System Success Rate |
| **Average Latency** | **3.92 seconds** | The average time taken for the full pipeline (Whisper local transcription + DeepSeek API extraction). | Inference Efficiency |

*(Note: The full evaluation data, including per-case scores and raw LLM output, is provided in `notebooks/final_evaluation_results.csv`.)*

### B. Qualitative Analysis and System Robustness

The failure cases highlight critical limitations that were addressed via Prompt Engineering and prove the system's ability to handle ambiguity.

* **System Successes (Robustness Evidence)**: The system successfully handled multi-transaction extraction from long, run-on sentences (e.g., Case 12) and correctly applied Few-Shot learning to extract complex amounts ($72.50). It also correctly filtered out non-spending speech (Case 06, 09, 14).

* **Specific Failure Modes (Error Analysis):**

    1.  **Length/Logic Mismatch**: The LLM occasionally failed to extract all items when the speech contained debt language ("I still owe her...") (Case 07), demonstrating a difficulty in distinguishing between a new expense and a debt repayment.
    2.  **Contextual Categorization**: The model failed to infer the context of secondary items, classifying a `Tip` associated with a `Meal` as the generic `Other` instead of `Food` (Case 10).
    3.  **Audio Collapse (OOD Noise)**: The most severe failures were due to the Whisper STT model failing dramatically under noisy or OOD conditions (Cases 17, 18, 19), resulting in completely nonsensical transcriptions (e.g., "My favorite was $6" instead of "Coffee was $6"). The LLM cannot recover from such catastrophic input errors.

---

## Individual Contributions

* This is a solo project

