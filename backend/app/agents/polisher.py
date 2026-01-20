from datetime import datetime
from ..core.llm import generate_text
from ..core.prompts import render_prompt

def polisher_agent(draft: str, critique_feedback: str, api_config: dict = None) -> str:
    """
    Step 4: Polish
    Final touches and slang injection.
    """
    if api_config is None:
        api_config = {}
    
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    context = {"current_time_str": datetime.now().isoformat()}
    system_prompt = render_prompt("polisher", context)

    user_prompt = f"""Draft: {draft}

Editor Feedback: {critique_feedback}

Please polish this content now."""
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.7,
            system_prompt=system_prompt
        )
        return response_text
    except Exception as e:
        return f"Error polishing content: {str(e)}"
