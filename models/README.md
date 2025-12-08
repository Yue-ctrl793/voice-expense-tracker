# Models Directory

This directory contains configuration and loading scripts for the AI models used in the Voice Expense Tracker.

## Model Architecture

1.  **Audio Processing :**
    * **Model:** OpenAI Whisper (Small)
    * **Storage:** The model weights are downloaded at runtime via the `whisper` library and cached locally (or on the cloud server). I did not commit the large binary files to Git to keep the repository lightweight.
    * **Loader:** See `audio_model.py`.

2.  **Logic Extraction (LLM):**
    * **Model:** DeepSeek V3 (via API)
    * **Configuration:** The system prompts, guardrails, and few-shot examples are managed in `llm_prompts.py`.