from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GOOGLE_GENAI_API_KEY"))

print("Listing available models...")
try:
    # distinct from the legacy syntax, checking unified client method
    # It seems the unified client might use a different way or just simple rest usage
    # But let's try the standard verify method
    for model in client.models.list(config={"page_size": 100}):
        print(f"Model: {model.name}")
except Exception as e:
    print(f"Error: {e}")
