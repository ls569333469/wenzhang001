from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi.responses import StreamingResponse
from ..core.llm import get_client, get_model_id, PROVIDER_CONFIGS
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class APIConfig(BaseModel):
    api_key: str = ""
    model_id: str = ""
    provider: str = "volcengine"

class RewriteRequest(BaseModel):
    selected_text: str
    instruction: str # "shorter", "longer", "fix_grammar", "polish", or custom
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    api_config: APIConfig = APIConfig()

@router.post("/api/rewrite")
async def rewrite_text(request: RewriteRequest):
    """
    Streamed partial rewrite API.
    """
    try:
        # 1. Setup Configuration
        provider = request.api_config.provider
        api_key = request.api_config.api_key
        model_id = request.api_config.model_id
        
        client = get_client(api_key=api_key, provider=provider)
        model = get_model_id(model_id=model_id, provider=provider)
        
        # 2. Construct Prompt
        system_prompt = (
            "You are a professional editor and writing assistant. "
            "Your task is to rewrite the user's selected text based on their instruction. "
            "Maintain the original tone and style unless asked to change it. "
            "Output ONLY the rewritten text, no explanations or pleasantries."
        )
        
        user_prompt = f"Instruction: {request.instruction}\n\n"
        
        if request.context_before:
            user_prompt += f"Context Before: ...{request.context_before[-200:]}\n"
        
        user_prompt += f"Selected Text: {request.selected_text}\n"
        
        if request.context_after:
            user_prompt += f"Context After: {request.context_after[:200]}...\n"
            
        print(f"[Rewrite] Prompting {provider} ({model})...")

        # 3. Stream Response
        async def stream_generator():
            try:
                # Handle Google Gemini
                if provider == "google":
                    from google.genai import types
                    contents = f"{system_prompt}\n\n{user_prompt}"
                    response = client.models.generate_content_stream(
                        model=model,
                        contents=contents,
                        config=types.GenerateContentConfig(temperature=0.7)
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                            
                # Handle OpenAI Compatible (Volc/OpenAI/DeepSeek)
                else:
                    stream = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        stream=True
                    )
                    
                    for chunk in stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content

            except Exception as e:
                error_msg = f"Error during generation: {str(e)}"
                logger.error(error_msg)
                yield f"[ERROR: {error_msg}]"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Rewrite endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
