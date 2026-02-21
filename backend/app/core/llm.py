"""
LLM Client Module - Multi-provider support
Supports: Volcengine (火山引擎), OpenAI, DeepSeek, Google Gemini

Based on official documentation:
- 火山引擎 API: https://ark.cn-beijing.volces.com/api/v3
- 使用标准 OpenAI SDK chat.completions.create 格式
"""
import os
import logging
from typing import Optional, Literal, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from .config import get_api_key as get_config_api_key

load_dotenv()
logger = logging.getLogger(__name__)

# 支持的提供商类型
ProviderType = Literal["google", "volcengine", "openai", "deepseek", "grok"]

# 提供商配置
PROVIDER_CONFIGS = {
    "volcengine": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "env_key": "ARK_API_KEY",
        "config_key": "doubao",
        "default_model": "doubao-seed-2-0-lite-260215",  # 豆包最新模型 (自动匹配)
        "available_models": [
            "deepseek-v3-2-251201",
            "doubao-seed-2-0-lite-260215",
            "doubao-1.5-pro-256k-250115",
            "doubao-1.5-lite-32k-250115"
        ]
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "config_key": "openai",
        "default_model": "gpt-4o",
        "available_models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "o1-preview",
            "o1-mini"
        ]
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "env_key": "DEEPSEEK_API_KEY",
        "config_key": "deepseek",
        "default_model": "deepseek-chat",
        "available_models": [
            "deepseek-chat",
            "deepseek-reasoner"
        ]
    },
    "google": {
        "env_key": "GOOGLE_GENAI_API_KEY",
        "config_key": "gemini",
        "default_model": "gemini-3-pro-preview",  # Gemini 3 Pro (最强)
        "available_models": [
            "gemini-3-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite"
        ]
    },
    "grok": {
        "base_url": "https://api.x.ai/v1",
        "env_key": "GROK_API_KEY",
        "config_key": "grok",
        "default_model": "grok-4-1-fast-reasoning",
        "available_models": [
            "grok-4-1-fast-reasoning",      # 4.1 高速推理 (2M上下文, $0.20/$0.50)
            "grok-4-1-fast-non-reasoning",   # 4.1 高速非推理
            "grok-4-fast-reasoning",         # 4.0 推理 (2M上下文)
            "grok-4-fast-non-reasoning",     # 4.0 非推理
            "grok-4-0709",                   # 4.0 旗舰 (256K, $3/$15)
            "grok-3-mini",                   # 3 轻量 (131K, $0.30/$0.50)
            "grok-3",                        # 3 标准 (131K, $3/$15)
        ]
    }
}

def get_client(api_key: Optional[str] = None, provider: str = "volcengine"):
    """
    Returns the appropriate LLM client based on provider.
    """
    config = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["volcengine"])
    
    # 获取 API Key
    if not api_key:
        # 优先使用 backend/config/user_config.json
        config_key = config.get("config_key", provider)
        api_key = get_config_api_key(config_key)
        
        # 再次检查环境变量 (get_config_api_key 内部已检查，但这作为双重保障或 legacy key 支持)
        if not api_key:
            api_key = os.environ.get(config["env_key"])
    
    if not api_key:
        # 友好错误提示
        raise ValueError(f"❌ API Key Missing: Please configure {provider} API key in Settings.")
    
    # Google Gemini 使用专用 SDK
    if provider == "google":
        from google import genai
        return genai.Client(api_key=api_key)
    
    # 其他提供商使用 OpenAI 兼容 SDK
    from openai import OpenAI
    return OpenAI(
        api_key=api_key,
        base_url=config.get("base_url")
    )


def get_model_id(model_id: Optional[str] = None, provider: str = "volcengine"):
    """
    Returns the model ID for the specified provider.
    """
    if model_id:
        return model_id
    
    config = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["volcengine"])
    return config["default_model"]



def _handle_llm_error(e: Exception, provider: str) -> str:
    """Transform raw LLM errors into user-friendly messages."""
    error_msg = str(e)
    
    if "401" in error_msg or "Invalid API Key" in error_msg:
        return f"❌ {provider} API Key 无效或未设置，请在设置页面检查配置。"
    
    if "429" in error_msg or "Too Many Requests" in error_msg:
        return f"⏳ {provider} API 调用限流 (Rate Limit)，请稍后重试。"
        
    if "500" in error_msg:
        return f"🔧 {provider} 服务端异常，我们将自动重试。"
        
    if "ConnectTimeout" in error_msg or "ReadTimeout" in error_msg:
        return f"⏱️ 连接 {provider} 超时，请检查网络设置。"
        
    return f"⚠️ {provider} 调用失败: {error_msg}"

@retry(
    stop=stop_after_attempt(1),  # 禁用重试，避免费用暴增 (原为 3 次)
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=before_sleep_log(logger, logging.INFO),
    reraise=True
)
def generate_text_with_retry(*args, **kwargs):
    """Wrapper to enable retry logic for generate_text internal call."""
    return _generate_text_impl(*args, **kwargs)

def _generate_text_impl(
    prompt: str,
    api_key: Optional[str] = None,
    model_id: Optional[str] = None,
    provider: str = "volcengine",
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096,
    extra_body: Optional[Dict[str, Any]] = None
) -> str:
    """Internal implementation of text generation."""
    # 调试输出
    print(f"[LLM DEBUG] Calling {provider} (model={model_id})...")
    
    client = get_client(api_key=api_key, provider=provider)
    model = get_model_id(model_id=model_id, provider=provider)
    
    # 增加超时设置 (长篇生成可能需要更长时间)
    timeout_config = {"timeout": 300.0}  # 5分钟超时
    
    # Google Gemini 使用不同的 API 格式
    if provider == "google":
        from google.genai import types
        
        contents = prompt
        if system_prompt:
            contents = f"{system_prompt}\n\n{prompt}"
        
        config = types.GenerateContentConfig(temperature=temperature)
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
        return response.text
    
    # OpenAI 兼容格式 (volcengine, openai, deepseek, grok)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    request_params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **timeout_config
    }
    
    # P16.1: 调试输出 max_tokens
    print(f"[LLM DEBUG] max_tokens={max_tokens} passed to API")
    
    if extra_body and provider == "volcengine":
        request_params["extra_body"] = extra_body
    
    response = client.chat.completions.create(**request_params)
    result = response.choices[0].message.content
    
    # P16.1: 硬性后处理截断 (LLM 可能不严格遵守 max_tokens)
    # 注意: 只对内容生成 (Writer/Polisher) 进行截断，不对结构化输出 (Critic JSON) 截断
    # 判断依据: max_tokens < 4096 表示是有意限制长度的内容生成场景
    max_chars = int(max_tokens * 0.7)
    if max_tokens < 4096 and len(result) > max_chars:
        print(f"[LLM DEBUG] ⚠️ Output exceeded max_tokens! Truncating {len(result)} → {max_chars} chars")
        # 找到最后一个句号/感叹号/问号截断，避免截断在句子中间
        truncated = result[:max_chars]
        for end_char in ['。', '！', '？', '\n']:
            last_pos = truncated.rfind(end_char)
            if last_pos > max_chars * 0.8:  # 保留至少 80% 的内容
                result = truncated[:last_pos + 1]
                break
        else:
            result = truncated + '...'
    
    return result

def generate_text(
    prompt: str,
    api_key: Optional[str] = None,
    model_id: Optional[str] = None,
    provider: str = "volcengine",
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096,
    extra_body: Optional[Dict[str, Any]] = None
) -> str:
    """
    Public interface with retry logic and error handling.
    """
    try:
        return generate_text_with_retry(
            prompt=prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=temperature,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            extra_body=extra_body
        )
    except Exception as e:
        friendly_msg = _handle_llm_error(e, provider)
        print(f"[LLM ERROR] {friendly_msg}")
        # 这里可以选择抛出原始异常或友好异常，目前选择抛出友好消息以便前端显示
        raise ValueError(friendly_msg)
