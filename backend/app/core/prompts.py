from pathlib import Path
from jinja2 import Template
from typing import Dict, Any

# 定位到 backend/data/prompts
PROMPTS_DIR = Path(__file__).parent.parent.parent / "data" / "prompts"

def get_prompt_path(agent_name: str) -> Path:
    return PROMPTS_DIR / f"{agent_name}.jinja2"

def load_template(agent_name: str) -> str:
    """Load the raw template string from file."""
    path = get_prompt_path(agent_name)
    if not path.exists():
        return f"Error: Template for {agent_name} not found."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_template(agent_name: str, content: str):
    """Save the raw template string to file."""
    path = get_prompt_path(agent_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def render_prompt(agent_name: str, context: Dict[str, Any]) -> str:
    """Load and render the template with the given context."""
    template_str = load_template(agent_name)
    try:
        template = Template(template_str)
        return template.render(**context)
    except Exception as e:
        return f"Error rendering prompt: {str(e)}"
