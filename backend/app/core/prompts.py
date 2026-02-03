from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
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


# P14: 支持子目录模板加载
def render_modular_prompt(template_path: str, context: Dict[str, Any]) -> str:
    """
    P14: 渲染子目录中的模板
    
    Args:
        template_path: 相对于 prompts 目录的路径，如 'writer/hot_take.jinja2'
        context: 模板上下文变量
    
    Returns:
        渲染后的提示词文本
    """
    full_path = PROMPTS_DIR / template_path
    if not full_path.exists():
        return f"Error: Template {template_path} not found."
    
    try:
        # 使用 Jinja2 Environment 支持 include
        env = Environment(loader=FileSystemLoader(str(PROMPTS_DIR)))
        template = env.get_template(template_path)
        return template.render(**context)
    except Exception as e:
        return f"Error rendering prompt: {str(e)}"


def get_writer_template_path(mode: str) -> str:
    """P14/P16: 根据 mode 获取 Writer 模板路径"""
    mode_template_map = {
        # P16: 新模式名
        "hot_take": "writer/hot_take.jinja2",
        "mid_article": "writer/quick_summary.jinja2",   # P16: 中篇 (原 quick_summary)
        "long_article": "writer/deep_analysis.jinja2",  # P16: 长篇 (原 deep_analysis)
        "tutorial": "writer/tutorial.jinja2",
        "rewrite": "writer/rewrite.jinja2",
        # P16: 向后兼容旧模式名
        "quick_summary": "writer/quick_summary.jinja2",
        "deep_analysis": "writer/deep_analysis.jinja2",
        "mid_take": "writer/quick_summary.jinja2",
    }
    return mode_template_map.get(mode, "writer.jinja2")  # fallback 到旧模板

