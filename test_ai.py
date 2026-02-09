import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    # Test common models
    test_models = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-1.0-pro',
        'gemini-1.5-pro',
        'gemini-flash-latest'
    ]
    
    print("--- Testing Models ---")
    for model_name in test_models:
        try:
            print(f"Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello in Thai")
            print(f"  SUCCESS! Response: {response.text.strip()}")
            # If successful, we found our model!
            break
        except Exception as e:
            print(f"  FAILED: {e}")
    print("--- Testing Complete ---")
