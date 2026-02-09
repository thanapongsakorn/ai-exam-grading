import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    try:
        print("--- Available Models ---")
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}, DisplayName: {m.display_name}")
        print("--- End of List ---")
    except Exception as e:
        print(f"Error listing models: {e}")
