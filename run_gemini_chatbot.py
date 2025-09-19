#!/usr/bin/env python3
"""
Script to run the FetiiAI chatbot with Gemini API
"""

import os
import subprocess
import sys

# Set the Gemini API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyDLB8NYTk_pSpWWXIgpEhXt-hoHTfVrC3E'

# Install required packages if not already installed
try:
    import google.generativeai
    print("✅ Google Generative AI package found")
except ImportError:
    print("📦 Installing Google Generative AI package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])

# Run the chatbot
print("🚀 Starting FetiiAI Chatbot with Gemini AI...")
print("🌐 The chatbot will open in your browser at http://localhost:8502")
print("💡 Ask questions like:")
print("   - How many groups went to Moody Center last month?")
print("   - What are the top drop-off spots for 18-24 year-olds on Saturday nights?")
print("   - When do large groups (6+ riders) typically ride downtown?")
print("\n" + "="*60)

# Import and run the chatbot
from fetii_chatbot import main

if __name__ == "__main__":
    main()