"""
Script to check available Google Gemini models
"""

import google.generativeai as genai
import os

def check_available_models():
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = input("Enter your Google API key: ")
    
    genai.configure(api_key=api_key)
    
    print("🔍 Available Google Gemini Models:")
    print("=" * 50)
    
    try:
        models = genai.list_models()
        
        for model in models:
            print(f"📋 Model: {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Supported Methods: {model.supported_generation_methods}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    check_available_models()
