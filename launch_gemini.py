import os
import sys

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyDLB8NYTk_pSpWWXIgpEhXt-hoHTfVrC3E'

# Import streamlit and run
import streamlit as st
from fetii_chatbot import main

if __name__ == "__main__":
    main()