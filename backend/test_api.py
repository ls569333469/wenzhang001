import os
import sys

# Add backend directory to sys.path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.core.llm import get_client

def test_generation():
    print("--- Testing Google GenAI SDK (Standard Models) ---")
    
    client = get_client()
    
    # List of models to try
    models_to_try = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]
    
    for model_id in models_to_try:
        print(f"\nTesting Model: {model_id}...")
        try:
            response = client.models.generate_content(
                model=model_id,
                contents="Hello World"
            )
            print(f"SUCCESS with {model_id}")
            print(f"Response: {response.text.strip()}")
            return # Stop on first success
        except Exception as e:
             print(f"FAILURE with {model_id}: {e}")

if __name__ == "__main__":
    test_generation()
