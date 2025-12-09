# Project Title: Voice Expense Tracker

Live Demo: https://voice-expense-tracker-efjeqy7kjlpzxawubbpswd.streamlit.app/

Short Description: An application that transcribes user voice recordings of expenses using the local Whisper model and uses the DeepSeek LLM for structured data extraction and categorization.

---

## What it Does

The Voice Expense Tracker is an AI application designed to streamline personal finance management through natural language processing. Instead of manual data entry, the system allows users to simply speak their expenses (e.g., "I spent 25 dollars on lunch and 50 on groceries"), automatically converting raw audio into structured financial data. The application operates on a two-stage pipeline:
First,  the system utilizes OpenAI's Whisper model to transcribe user audio. Second, the transcribed text is processed by the DeepSeek V3 Large Language Model. Unlike simple keyword matching, the LLM employs advanced reasoning to precisely extract entities and monetary amounts while intelligently mapping items to predefined categories. Beyond basic extraction, the model actively performs logic correction to resolve speech errors and enforces safety guardrails to filter out toxic or irrelevant content. Once processed, the data is presented in an editable review table for user to edit. Then the confirmed expenses are stored in a persistent session history and visualized through dynamic charts to provide immediate insights into spending habits.

---

## Quick Start


The fastest way to test the application is via the live deployment: https://voice-expense-tracker-efjeqy7kjlpzxawubbpswd.streamlit.app/
(No installation required. Works in your browser.)

Note on Resource Limits: The live demo is hosted on the Streamlit Community Cloud (Free Tier). Due to memory constraints, I choose the Whisper base model. For high-fidelity transcription using the small or medium models, running the application locally is recommended (see SETUP.md).

To run locally:

1.  **Clone the Install:**
    ```bash
    git clone https://github.com/Yue-ctrl793/voice-expense-tracker.git
    cd voice-expense-tracker
    pip install -r requirements.txt
    ```

2.  **Configure Secrets:**

    Create a .streamlit/secrets.toml file and add your DeepSeek API Key:
    ```bash
    DEEPSEEK_API_KEY = "sk-72dffba7962240dab3ef69f92229d83e"
    ```

3.  **Run the Application:**
    ```bash
    streamlit run src/app.py
    ```
    The application will open in your web browser.

    Note: Local execution requires FFmpeg to be installed on your system. For detailed installation instructions (Mac/Windows/Linux) and troubleshooting, please refer to SETUP.md.

---

## Video Links


* **Project Demo:** https://duke.box.com/s/z25re319cqnq4yyua5p1xzve2skbeyy2
* **Technical Walkthrough:** https://duke.box.com/s/nb67mggz5p8fh2ht6aj7uel3usg01vyh

---

## Evaluation & Results

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

### 2. Phase I Results (Quantitative and Qualitative)

To evaluate the reasoning engine (DeepSeek V3) in isolation, I tested **1000 diverse synthetic scenarios** featuring complex logic, self-corrections (e.g., "Wait, no..."), and variable sentence structures.

**Quantitative Results**

| Metric | Result | Analysis |
| :--- | :--- | :--- |
| **Sample Size** | 1000 | Statistically significant volume. |
| **Average Latency** | **2.95s** | High efficiency for a large language model. |
| **Average Category Accuracy** | **88.94%** | **Excellent.** Indicates the model has strong semantic understanding and correctly maps items to their logical categories almost 90% of the time. |
| **Average Slot Accuracy** | **80.58%** | **Good.** The model captures the majority of field-level details correctly. |
| **Average Final JSON Accuracy** | **60.40%** | **Moderate.** The gap between Category Accuracy and Final Accuracy highlights the strictness of the exact-match metric. |

**Error Analysis**

To understand the nature of the 396 failure cases (where Final Accuracy < 100%), I developed a programmatic classifier to categorize errors into three distinct types.

| Error Type | Count | Percentage | Impact Level |
| :--- | :--- | :--- | :--- |
| **Item String Mismatch (Logic Correct)** | 265 | 66.9% | Low |
| **Category Classification Error** | 112 | 28.3% | Medium |
| **Length Mismatch (Hallucination)** | 19 | 4.8% | High |

**Key Insights**

1.  **Dominance of Benign Errors (66.9%):**
    The majority of recorded "failures" are merely string formatting differences (e.g., extracting "Apple" vs. "Red Apple") where the logic and category were actually correct.

2.  **Wrong Categorization (28.3%):**
    Category errors often stemmed from ambiguous items (e.g., classifying *Gift* as *Other* instead of *Retail*). Given the high overall Category Accuracy (88.94%), the model shows strong adherence to financial taxonomy, with errors largely falling into defensible ambiguity.

3.  **Low Hallucination Rate (< 2%):**
    Only 19 cases out of the full 1000 dataset (1.9%) resulted in missing or hallucinated items. This proves the system is reliable in capturing the correct number of transactions, which is critical for a bookkeeping application.

**Conclusion:**
Phase I confirms that DeepSeek V3 acts as a robust reasoning engine. The discrepancy between the high Category/Slot Accuracy and the lower Final Accuracy is primarily an artifact of strict string matching rather than a failure of logic.

### 3. Phase II Results (Quantitative)

The full pipeline was tested on 50 diverse audio clips.

| Metric | Result | Analysis |
| :--- | :--- | :--- |
| **Average System Latency** | **3.83s** | Performance is acceptable for real-time user interaction. |
| **Average Slot Accuracy** | **80.44%** | **High.** Indicates the system correctly identifies individual fields (Item/Amount) in the majority of cases, even if the full JSON structure is not a perfect match. |
| **Average Category Accuracy**| **76.33%** | **High.** Shows that the LLM's reasoning and classification logic remains robust even when minor transcription errors occur. |
| **Average Final JSON Accuracy** | **58.00%** | **Moderate.** The score is relatively lower, see failure analysis. |


#### Performance by Category (Summary)

The system demonstrated exceptional performance in **Safety (Guardrails)** and **Negative Constraints**, while noise robustness remains the primary area for improvement. Notably, complex logic tasks required significantly higher latency (4.78s) compared to quick safety rejections (2.86s).

| Type | Slot Acc | Category Acc | Final JSON Acc | Latency (s) | Count | Performance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Guardrail_Toxic** | 1.00 | 1.00 | 1.00 | 2.86s | 4 | Perfect |
| **Edge_Negative** | 1.00 | 1.00 | 1.00 | 3.17s | 3 | Perfect |
| **Edge_Unit** | 0.87 | 0.80 | 0.60 | 3.97s | 5 | Good |
| **Edge_Logic** | 0.86 | 0.65 | 0.50 | 4.78s | 8 | Good |
| **Edge_Category** | 0.83 | 1.00 | 0.50 | 3.24s | 2 | Good |
| **Normal** | 0.81 | 0.75 | 0.65 | 3.76s | 20 | Solid |
| **Edge_Accent** | 0.67 | 1.00 | 0.00 | 3.31s | 2 | Challenging |
| **Edge_Noise** | 0.47 | 0.50 | 0.17 | 4.05s | 6 | Weak Point |

### 4. Qualitative Analysis

The detailed failure table is in notebooks/evaluation.ipynb.

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

### 6. Overall Conclusion

* The results confirm that the Reasoning Engine (DeepSeek V3) is highly reliable, achieving high accuracy in categorization. The primary bottleneck is not the LLM's logic, but the **ASR (Whisper Small) sensitivity** to environmental noise.

* While the strict "Final JSON Accuracy" sits around 60%, the high **Slot Accuracy (~80%)** indicates that the system is functionally viable. In the vast majority of cases, the user receives a correct extraction that requires zero or minimal editing, reducing the friction of manual data entry.


* The specific failures in subjective categorization (e.g., *Hotel* as *Retail* vs. *Other*) validate the design decision to include **Human-in-the-Loop** editing in the UI. Since personal finance taxonomies are inherently subjective, a fully automated system is less desirable than an intelligent assistant that proposes high-confidence defaults.

* Moving forward, the system's robustness could be significantly improved by integrating a Voice Activity Detection layer to pre-filter noise or by fine-tuning the ASR model on accented financial speech.


---

## Individual Contributions

* This is a solo project

