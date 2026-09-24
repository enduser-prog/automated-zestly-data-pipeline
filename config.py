import os
from dotenv import load_dotenv

load_dotenv()


def _get(key, default=""):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


DB_NAME = _get("DB_NAME", "defaultdb")
DB_USER = _get("DB_USER", "avnadmin")
DB_PASSWORD = _get("DB_PASSWORD", "")
DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = _get("DB_PORT", "5432")
DB_SSLMODE = _get("DB_SSLMODE", "require")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode={DB_SSLMODE}"
)
