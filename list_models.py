import google.generativeai as genai
import os
from config.config import settings

genai.configure(api_key=settings.LLM_API_KEY)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
