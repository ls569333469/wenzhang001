from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from typing import Dict, Any

# P21: 禁用词库注入
from .forbidden_patterns import load_forbidden_patterns

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
    # P21: 自动注入禁用词库
    if 'forbidden_patterns' not in context:
        context['forbidden_patterns'] = load_forbidden_patterns()
    
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
    
    # P21: 自动注入禁用词库
    if 'forbidden_patterns' not in context:
        context['forbidden_patterns'] = load_forbidden_patterns()
    
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
        # P18: 标准模式 (指向 Phase 1 新建的专用模板)
        "hot_take": "writer/hot_take.jinja2",
        "short_article": "writer/short_article.jinja2",
        "mid_article": "writer/mid_article.jinja2",
        "long_article": "writer/long_article.jinja2",
        "tutorial": "writer/tutorial.jinja2",
        "bullish_take": "writer/bullish_take.jinja2",
        "kaito_yap": "writer/kaito_yap.jinja2",
        "project_research": "writer/project_research.jinja2",
    }
    return mode_template_map.get(mode, "writer.jinja2")  # fallback


def get_critic_template_path(mode: str) -> str:
    """P27: 根据 mode 获取 Critic 模板路径"""
    mode_template_map = {
        "short_article": "critic/short_article.jinja2",
        "mid_article": "critic/mid_article.jinja2",
        "long_article": "critic/long_article.jinja2",
        "tutorial": "critic/tutorial.jinja2",
        "bullish_take": "critic/bullish_take.jinja2",
        "kaito_yap": "critic/kaito_yap.jinja2",
        "project_research": "critic/project_research.jinja2",
        # hot_take: skip_critic, 不需要模板
    }
    return mode_template_map.get(mode, "shared/base_critic.jinja2")  # fallback


def get_polisher_template_path(mode: str) -> str:
    """P27: 根据 mode 获取 Polisher 模板路径"""
    mode_template_map = {
        "short_article": "polisher/short_article.jinja2",
        "mid_article": "polisher/mid_article.jinja2",
        "long_article": "polisher/long_article.jinja2",
        "tutorial": "polisher/tutorial.jinja2",
        "bullish_take": "polisher/bullish_take.jinja2",
        "kaito_yap": "polisher/kaito_yap.jinja2",
        "project_research": "polisher/project_research.jinja2",
        # hot_take: skip_polisher, 不需要模板
    }
    return mode_template_map.get(mode, "shared/base_polisher.jinja2")  # fallback


