import os
import streamlit as st
import google.generativeai as genai

def setup_gemini_api():
    api_key = None
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("🔑 Google API Key Required")
        api_key = st.text_input("Enter your Google API key:", type="password")
        if not api_key:
            st.stop()

    genai.configure(api_key=api_key)
    return api_key
