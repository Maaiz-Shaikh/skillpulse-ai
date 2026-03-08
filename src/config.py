import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str, default: str = None) -> str:
    """Gets a secret from Streamlit secrets (Cloud) or environment variables (Local)."""
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

ADZUNA_APP_ID = get_secret("ADZUNA_APP_ID")
ADZUNA_APP_KEY = get_secret("ADZUNA_APP_KEY")
LLM_PROVIDER = get_secret("LLM_PROVIDER", "openrouter")
LLM_API_KEY = get_secret("LLM_API_KEY")
LLM_MODEL = get_secret("LLM_MODEL")
