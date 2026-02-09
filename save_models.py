import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    with open("models_list.txt", "w") as f:
        f.write("Error: GEMINI_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    try:
        models = genai.list_models()
        with open("models_list.txt", "w", encoding='utf-8') as f:
            f.write("--- Available Models ---\n")
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"{m.name}\n")
            f.write("--- End of List ---\n")
        print("Model list saved to models_list.txt")
    except Exception as e:
        with open("models_list.txt", "w") as f:
            f.write(f"Error listing models: {e}")
