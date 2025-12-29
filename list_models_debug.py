import google.generativeai as genai
import os
from config.config import settings

genai.configure(api_key=settings.LLM_API_KEY)

with open("models_list.txt", "w", encoding="utf-8") as f:
    try:
        f.write("Listing models:\n")
        for m in genai.list_models():
            f.write(f"{m.name}: {m.supported_generation_methods}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
