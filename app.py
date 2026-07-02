"""
Streamlit & API-Integration

Starten mit:
    uv run streamlit run app.py
"""
import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

st.title("Semesterprojekt - Buchungssystem")

# ---------------------------------------------------------------------------
# Daten laden und anzeigen
# ---------------------------------------------------------------------------
if st.button("Buchungen laden"):
    try:
        response = requests.get(f"{API_URL}/bookings")
        df = pd.DataFrame(response.json())
        st.dataframe(df)
    except requests.exceptions.ConnectionError:
     st.error("Backend nicht erreichbar – ist der FastAPI-Server gestartet?")
    st.write(f"Insgesamt {len(df)} Buchungen")


