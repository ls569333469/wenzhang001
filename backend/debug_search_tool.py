from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# Load env variables (API Key)
load_dotenv(dotenv_path="backend/.env")

def debug_search():
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("Error: API Key not found.")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-2.0-flash-exp" # Or gemini-1.5-flash

    print(f"--- Debugging Google Search with {model_id} ---")
    
    prompt = "What is the specific price of Bitcoin right now in USD? Be precise."

    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        response_mime_type="text/plain" # Use text first to see full reasoning
    )

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )
        
        print("\n--- Response Text ---")
        print(response.text)
        
        print("\n--- Grounding Metadata ---")
        # Check if search actually happened
        if response.candidates and response.candidates[0].grounding_metadata:
             gm = response.candidates[0].grounding_metadata
             print(f"Search Entry Point: {gm.search_entry_point}")
             print(f"Grounding Chunks: {len(gm.grounding_chunks) if gm.grounding_chunks else 0}")
             if gm.grounding_chunks:
                 print(f"First Chunk: {gm.grounding_chunks[0].web.title}")
        else:
            print("NO GROUNDING METADATA FOUND. Search failed.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_search()
