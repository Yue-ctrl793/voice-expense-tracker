# AI Voice Expense Tracker: Voice-to-Data Pipeline

Live Demo: https://voice-expense-tracker-efjeqy7kjlpzxawubbpswd.streamlit.app/

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


* **Project Demo (3-5 min):** [Link to YouTube/Vimeo Demo Video]
* **Technical Walkthrough (5-10 min):** [Link to YouTube/Vimeo Technical Walkthrough Video]

---

## ## Evaluation & Results

I employed a Dual-Stream Evaluation Strategy, isolating the reasoning capabilities of the LLM from the acoustic robustness of the Speech to Text model.

### 1. Methodology

The evaluation was conducted in two distinct phases:

* **Phase I: Logic at Scale (DeepSeek Only)**
    * **Dataset:** 1000 synthetic text samples generated via DeepSeek.
    * **Complexity:** Included complex sentence structures, self-corrections (e.g., "I spent 40, wait, actually 50..."), and multi-item lists.
    * **Goal:** To statistically validate DeepSeek's ability to extract JSON and follow prompt instructions without the variable of speech recognition errors.

* **Phase II: Pipeline Robustness**
    * **Dataset:** 50 manual audio recordings created for this project.
    * **Composition:** 20 Normal cases and 30 Edge cases (including Accents, Background Noise, Logic Switches, Toxic Content, and Mixed Units).
    * **Goal:** To test the full pipeline (Whisper Small + DeepSeek V3) in real-world scenarios.
    * **Metric:** I utilized Slot Accuracy (field-level correctness), Final JSON Accuracy (exact string match) and latency.

### 3. Phase II Results (Quantitative)

The full pipeline was tested on 50 diverse audio clips.

| Metric | Result | Analysis |
| :--- | :--- | :--- |
| **Average System Latency** | **3.83s** | Performance is acceptable for real-time user interaction. |
| **Average Slot Accuracy** | **80.44%** | **High.** Indicates the system correctly identifies individual fields (Item/Amount) in the majority of cases, even if the full JSON structure is not a perfect match. |
| **Average Final JSON Accuracy** | **58.00%** | **Moderate.** The score is relatively lower, see failure analysis. |

#### Performance by Category (Summary)

The system demonstrated exceptional performance in **Safety (Guardrails)** and **Negative Constraints**, while noise robustness remains the primary area for improvement.

| Type | Slot Acc | Final JSON Acc | Count | Performance |
| :--- | :--- | :--- | :--- | :--- |
| **Guardrail_Toxic** | 1.00 | 1.00 | 4 | Perfect |
| **Edge_Negative** | 1.00 | 1.00 | 3 | Perfect |
| **Edge_Logic** | 0.86 | 0.50 | 8 | Good |
| **Edge_Unit** | 0.87 | 0.60 | 5 | Good |
| **Edge_Category** | 0.83 | 0.50 | 2 | Good |
| **Normal** | 0.81 | 0.65 | 20 | Solid |
| **Edge_Accent** | 0.67 | 0.00 | 2 | Challenging |
| **Edge_Noise** | 0.47 | 0.17 | 6 | Weak Point |

### 4. Qualitative Analysis

#### Success Analysis: Model Strengths

1.  **Robust Guardrails & Safety:**
    The system achieved **100% accuracy** in blocking toxic or illegal content.
    * *Input:* "I spent $500 on drugs", "Bought a gun", "Fake ID".
    * *Result:* The model correctly returned `[]` (Empty List), adhering strictly to the safety system prompt.

2.  **Negative Constraints & Filtering:**
    The model successfully ignored non-expense related speech.
    * *Input:* "I spent nothing today" or "I hope it doesn't snow".
    * *Result:* Correctly returned `[]`, proving the model does not "hallucinate" expenses where there are none.

3.  **Complex Logic & Self-Correction:**
    DeepSeek demonstrated strong reasoning capabilities in handling user corrections and parsing logic.
    * *Correction:* "Bought a monitor for 150... wait, actually it was 200." -> Output: **200** (Correct).
    * *Separation:* "Taxi was $5 and toll was $3." -> Correctly extracted both items separately.

4.  **Unit & Format Handling:**
    The model showed high intelligence in handling diverse inputs.
    * *Units:* "2K" -> Output **2000.00**; "120 bucks" -> Output **120.00**.
    * *Brand Recognition:* Correctly identified "Spotify" and "Uber" as specific items.

### 5. Failure Analysis

**A. Whisper ASR Errors (Noise & Accent)**


The primary bottleneck in low-accuracy cases was the Speech-to-Text(Whisper) layer, specifically in noisy environments or with heavy accents.
* *Noise:* "Tip for **five**" was transcribed as "Tip for **fire**"; "Lunch" became "Mine"; "Coffee" became "fee". 
* *Accent:* "Three fiddy" ($3.50) was transcribed as "350", leading to a massive outlier in amount.

**B. Subjective Categorization & Contextual Logic (DeepSeek)**

Failures in this domain fell into two distinct categories: serious contextual errors and understandable definitional ambiguities.

* **1. Contextual Isolation (Logic Error):**


    The model occasionally failed to link dependent items.
    * *Example:* "Tip for meal" was classified as *Other*. The model failed to associate the "tip" with the "meal" context, missing the obvious connection to the *Food* category.

* **2. Domain Misclassification (Model Error):**


    In these cases, the model made objectively incorrect classifications based on a misunderstanding of expense tracking norms.
    * "Dog food" was classified as *Food* (literal interpretation). In personal finance, "Food" implies human dining/groceries, while pet supplies should be *Retail* or *Personal Care*.
    * "Hotel" was classified as *Retail*. This is factually incorrect as hotels are hospitality services, not retail goods.

* **3. Definitional Ambiguity (Subjective):**


    Some discrepancies arose from genuine overlap in category definitions.
    * "Laptop" was classified as *Retail* (correct as a purchase type), whereas ground truth expected *Other* (due to high value).
    * "Used car" was classified as *Transport* (correct as usage), whereas ground truth expected *Retail* (transaction type).

* **Mitigation Strategy (UI Design):**


    Acknowledging that categorization is inherently subjective, the application UI was explicitly designed with **manual edit functionality**. This allows users to override reasonable but non-preferred model predictions (e.g., changing "Used car" from *Transport* to *Retail*), ensuring the system adapts to individual user habits.

**C. String Matching**


The quantitative score was penalized by minor string mismatches even when the extraction logic was functionally correct.
* *Example:* Ground truth "Donation" vs Actual "Donation to charity".
* *Example:* Ground truth "Sushi" vs Actual "Sushi dinner".


---

## Individual Contributions

* This is a solo project

