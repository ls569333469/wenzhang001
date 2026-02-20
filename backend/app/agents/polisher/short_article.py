"""
P26: 短篇润色官 — 代码预扫 + LLM 最小修复
职责：AI禁用词检测 + 最小改动修复 + 标点后处理
"""
import re
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_prompt
from app.core.forbidden_patterns import get_all_forbidden_words


def _scan_forbidden_words(text: str) -> list:
    """
    代码扫描禁用词，返回命中列表
    
    Returns:
        [{"word": "赛道", "sentence": "加密赛道最资深的玩家"}, ...]
    """
    all_words = get_all_forbidden_words()
    hits = []
    
    # 按句号/感叹号/问号/换行 分句
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    for word in all_words:
        if word in text:
            # 找到包含该词的句子
            for sentence in sentences:
                if word in sentence:
                    hits.append({"word": word, "sentence": sentence})
                    break
            else:
                # 没找到具体句子，给整段上下文
                idx = text.find(word)
                context = text[max(0, idx-15):idx+len(word)+15]
                hits.append({"word": word, "sentence": context})
    
    return hits


def _post_process(text: str) -> str:
    """标点后处理"""
    if not text:
        return text
    text = re.sub(r'——', '，', text)
    text = re.sub(r'—', '，', text)
    text = re.sub(r'；', '，', text)
    return text


def _split_versions(draft: str) -> list:
    """
    将多版本 draft 按 '---' 分隔符拆分为独立版本
    如果没有分隔符，返回整篇作为单版本
    """
    # 按 '---' 或 '***' 分隔（markdown 水平线）
    parts = re.split(r'\n\s*---\s*\n|\n\s*\*\*\*\s*\n', draft)
    # 过滤空块
    versions = [p.strip() for p in parts if p.strip()]
    return versions if versions else [draft]


def _polish_single_version(version_text: str, api_config: dict,
                            length_constraints: dict) -> str:
    """
    对单个版本做：代码扫描 → LLM最小修复 → 标点后处理
    """
    # 代码扫描
    hits = _scan_forbidden_words(version_text)
    
    if not hits:
        return _post_process(version_text)
    
    print(f"--- [P26 Polisher] ⚠️ 命中 {len(hits)} 个禁用词: {[h['word'] for h in hits]} ---")
    
    provider = api_config.get("provider", "volcengine")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    
    context = {
        "current_time_str": datetime.now().isoformat(),
        "draft": version_text,
        "hits": hits,
    }
    
    system_prompt = render_prompt("polisher/short_article", context)
    user_prompt = "请修改上述命中的禁用词，只动最少的字。直接输出完整文章。"
    
    # 单版本 token 上限：按该版本字数计算，留足余量
    version_chars = len(version_text)
    calculated_max_tokens = min(int(version_chars * 2), 2048)
    
    try:
        polished = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            model_id=model_id,
            provider=provider,
            temperature=0.3,  # 低温度，减少创造性改写
            system_prompt=system_prompt,
            max_tokens=calculated_max_tokens,
        )
        
        polished = _post_process(polished)
        
        # 改写后再扫一次
        remaining = _scan_forbidden_words(polished)
        if remaining:
            print(f"--- [P26 Polisher] ⚠️ 修复后仍有 {len(remaining)} 个禁用词: {[h['word'] for h in remaining]} ---")
        else:
            print("--- [P26 Polisher] ✅ 修复成功，禁用词已清除 ---")
        
        return polished
        
    except Exception as e:
        print(f"--- [P26 Polisher] ❌ LLM调用失败: {e}，返回标点后处理版 ---")
        return _post_process(version_text)


def short_article_polisher(draft: str, critique_feedback: str, api_config: dict = None,
                           custom_prompts: dict = None, mode: str = "short_article",
                           length_constraints: dict = None) -> str:
    """
    P26: 短篇润色官 — 代码预扫 + LLM 最小修复
    
    流程:
    1. 按 '---' 拆分多版本（如有）
    2. 逐版本：代码扫描 → 有命中才调LLM → 标点后处理
    3. 合并所有版本输出
    """
    if api_config is None:
        api_config = {}
    if length_constraints is None:
        length_constraints = {"min": 50, "max": 300, "target": 200}
    
    # Step 1: 拆分版本
    versions = _split_versions(draft)
    print(f"--- [P26 Polisher] 检测到 {len(versions)} 个版本 ---")
    
    # Step 2: 逐版本处理
    polished_versions = []
    for i, version in enumerate(versions):
        print(f"--- [P26 Polisher] 处理版本 {i+1}/{len(versions)} ---")
        # 剥离版本标题头（如 "## 版本1：机构信号版"），避免 LLM 修复时吞掉标题
        header = ""
        body = version
        header_match = re.match(r'^(##\s*版本\d+[：:].+)\n', version)
        if header_match:
            header = header_match.group(1) + "\n\n"
            body = version[header_match.end():].lstrip()
        result = _polish_single_version(body, api_config, length_constraints)
        polished_versions.append(header + result)
    
    # Step 3: 合并输出（用 --- 分隔）
    if len(polished_versions) == 1:
        return polished_versions[0]
    
    return "\n\n---\n\n".join(polished_versions)
