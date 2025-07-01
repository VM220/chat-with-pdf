"""
Quick script to install the correct packages for Google Gemini integration
"""

import subprocess
import sys

def install_correct_packages():
    """Install the correct packages for Google integration"""
    packages = [
        "langchain-google-genai",
        "langchain-community", 
        "google-generativeai"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--upgrade"])
            print(f"✅ {package} installed successfully!")
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")

if __name__ == "__main__":
    print("🔧 Installing correct packages for Google Gemini...")
    install_correct_packages()
    print("✅ Done! Now try running: python -m streamlit run app.py")
