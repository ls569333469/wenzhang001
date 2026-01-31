from datetime import datetime
import json
from ..core.llm import generate_text
from ..core.prompts import render_prompt
from ..graph import calculate_length

def critic_agent(draft: str, mode: str, api_config: dict = None, 
                 length: str = "thread", style: str = "auto") -> tuple[int, str]:
    """
    Step 3: Critique
    Reviews the draft and provides a score (0-100) and feedback.
    Now includes mode/length/style constraints for accurate scoring.
    """
    if api_config is None:
        api_config = {}
    
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    # 计算字数约束和当前字数
    length_constraints = calculate_length(length)
    word_count = len(draft)
    
    context = {
        "current_time_str": datetime.now().isoformat(),
        "mode": mode,
        "length": length,
        "length_constraints": length_constraints,
        "style": style,
        "word_count": word_count
    }
    system_prompt = render_prompt("critic", context)

    user_prompt = f"""Draft Content:
{draft}

Please review and score this content based on the criteria in your system prompt."""
    
    try:
        response_text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.1,
            system_prompt=system_prompt
        )
        
        # Parse result
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(text)
        return result.get("score", 0), result.get("feedback", "No feedback provided.")
        
    except Exception as e:
        print(f"Critic Error: {e}")
        return 0, f"Critic error: {str(e)}"
