#!/usr/bin/env python3
"""
Install spaCy and download the English model
Run this script to set up spaCy for content analysis
"""
import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Installing spaCy and English model for content analysis...")
    print()
    
    # Install spaCy
    print("1. Installing spaCy...")
    if not run_command("pip install spacy"):
        print("❌ Failed to install spaCy")
        return False
    
    # Download English model
    print("\n2. Downloading English model...")
    if not run_command("python -m spacy download en_core_web_sm"):
        print("❌ Failed to download English model")
        return False
    
    # Verify installation
    print("\n3. Verifying installation...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy installation verified")
        print(f"✅ English model loaded successfully")
        
        # Test basic functionality
        doc = nlp("This is a test sentence.")
        print(f"✅ Test analysis: {len(doc)} tokens processed")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    print("\n🎉 spaCy installation completed successfully!")
    print("You can now use the content analysis functionality.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation failed!")
        sys.exit(1)
    else:
        print("\n✅ Ready to analyze content!")
