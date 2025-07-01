"""
Windows-specific setup script for PDF Q&A Bot
Handles Windows compatibility issues
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages with Windows compatibility"""
    print("🚀 Installing packages for Windows...")
    
    # Install packages one by one to handle potential conflicts
    packages = [
        "streamlit>=1.28.0",
        "python-dotenv>=1.0.0",
        "google-generativeai>=0.3.0",
        "pypdf>=3.17.0",
        "numpy>=1.21.0,<1.25.0",  # Use older numpy to avoid compilation issues
        "pandas>=1.3.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-google-genai>=0.0.6",
        "chromadb>=0.4.15",
        "tiktoken>=0.5.0"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e}")
            print("Trying alternative installation...")
            try:
                # Try with --no-build-isolation for problematic packages
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--no-build-isolation"])
                print(f"✅ {package} installed with alternative method!")
            except:
                print(f"⚠️ Could not install {package}. You may need to install it manually.")

def setup_directories():
    """Create necessary directories"""
    directories = ["chroma_db", ".streamlit"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def create_secrets_file():
    """Create secrets.toml template"""
    secrets_path = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_path):
        with open(secrets_path, "w") as f:
            f.write('# Add your Google API key here\n')
            f.write('GOOGLE_API_KEY = "your-google-api-key-here"\n')
        print(f"📝 Created {secrets_path} template")
        print("⚠️ Please edit this file and add your actual Google API key!")

def main():
    print("🚀 Setting up PDF Q&A Bot for Windows")
    print("=" * 50)
    
    # Upgrade pip first
    print("Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    install_requirements()
    setup_directories()
    create_secrets_file()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .streamlit/secrets.toml and add your Google API key")
    print("2. Run: streamlit run app.py")
    print("3. Upload a PDF file and start chatting!")

if __name__ == "__main__":
    main()
