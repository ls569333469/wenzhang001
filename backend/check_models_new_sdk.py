import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_models():
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("--- Listing Available Models (New SDK) ---")
    try:
        # Pager object, need to iterate
        for model in client.models.list():
            print(f"Model: {model.name}")
            # print(f"  - Logic: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
