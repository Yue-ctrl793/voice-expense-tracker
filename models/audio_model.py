import whisper
import streamlit as st

# AI generated: google gemini 2
@st.cache_resource
def load_whisper_model(model_size="base"):
    """
    Loads and caches the Whisper model to prevent reloading on every interaction.
    Args:
        model_size (str): Size of the Whisper model (tiny, base, small, medium, large).
    Returns:
        The loaded Whisper model instance.
    """
    print(f"Loading Whisper model: {model_size}...")
    model = whisper.load_model(model_size)
    return model