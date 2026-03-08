"""
币安广场 Writer - P34
3 版本生成：策略官 3 个方案 → 写手分别执行
900 字限制，专业/教育向调性
"""
from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_modular_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from app.services.google_sheets_source import google_sheets_source
import re
import json
import time
import logging

logger = logging.getLogger(__name__)


def _extract_plans(strategy_json: str) -> list:
    """从策略官输出提取版本方案"""
    try:
        obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
        plans = obj.get("plans", [])
        if isinstance(plans, list) and len(plans) > 0:
            print(f"--- [P34] ✅ 从策略官提取到 {len(plans)} 个广场方案 ---")
            return plans[:3]
        raise ValueError(f"策略官输出plans为空: {plans}")
    except json.JSONDecodeError as e:
        raise ValueError(f"策略官JSON解析失败: {e}")


def _get_rag_samples(query_text: str = "") -> str:
    """获取语义匹配风格样本（Chroma 优先，回退到随机）"""
    try:
        if query_text:
            # P34: 尝试 Chroma 语义匹配
            samples = google_sheets_source.get_semantic_samples(
                query_text=query_text,
                style="banfo",
                count=2,
            )
        else:
            samples = google_sheets_source.get_samples(
                style="banfo", emotion="积极", count=2
            )
        if not samples:
            return ""
        parts = []
        for i, s in enumerate(samples, 1):
            content = s.get("content", "")
            if content:
                parts.append(f"--- 样本({s.get('snippet_type','')}) ---\n{content[:300]}")
        return "\n\n".join(parts)
    except Exception as e:
        print(f"[binance_square] RAG sample fetch failed: {e}")
        return ""


def _get_voice_anchors(query_text: str) -> list:
    """P34: 从 Chroma 获取声调锚定 (最近发布的帖子)"""
    try:
        from app.services.chroma_service import get_chroma_service
        chroma = get_chroma_service()
        posts = chroma.get_recent_posts(
            query_text=query_text,
            n_results=3,
            platform="binance_square",
        )
        return [p["content"] for p in posts if p.get("content")]
    except Exception as e:
        print(f"[binance_square] Voice anchor fetch failed: {e}")
        return []


def _get_project_context(raw_input: str, n_tweets: int = 5, n_website: int = 3) -> str:
    """
    P34 Phase 2: 从 Chroma Cloud 获取项目上下文
    自动搜索推文和官网数据，拼接成 project_context
    """
    try:
        import os
        import chromadb
        from dotenv import load_dotenv
        from pathlib import Path
        load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

        api_key = os.getenv("CHROMA_CLOUD_API_KEY")
        tenant = os.getenv("CHROMA_CLOUD_TENANT")
        database = os.getenv("CHROMA_CLOUD_DATABASE")

        if not all([api_key, tenant, database]):
            logger.warning("[P34] Chroma Cloud credentials not configured")
            return ""

        client = chromadb.CloudClient(tenant=tenant, database=database, api_key=api_key)
        parts = []

        # 搜索推文 (用英文查询效果更好)
        # 从 raw_input 提取关键词作为查询
        query = raw_input[:200]  # 取前200字作为查询文本
        
        # 遍历所有 *_tweets collection
        for col in client.list_collections():
            if col.name.endswith("_tweets") and col.count() > 0:
                results = col.query(query_texts=[query], n_results=n_tweets)
                if results and results["documents"] and results["documents"][0]:
                    parts.append(f"\n--- 官推数据 ({col.name}, {len(results['documents'][0])}条) ---")
                    for i, doc in enumerate(results["documents"][0]):
                        meta = results["metadatas"][0][i] if results["metadatas"] else {}
                        created = meta.get("created_at", "")
                        parts.append(f"[{created[:20]}] {doc}")

        # 搜索官网数据
        try:
            website_col = client.get_collection("fabric_foundation")
            if website_col.count() > 0:
                results = website_col.query(query_texts=[query], n_results=n_website)
                if results and results["documents"] and results["documents"][0]:
                    parts.append(f"\n--- 官网数据 ({n_website}条) ---")
                    for doc in results["documents"][0]:
                        # 去掉 HTML 噪声
                        clean = doc.replace("![Logo]", "").strip()[:300]
                        if clean:
                            parts.append(clean)
        except Exception:
            pass  # collection 不存在时跳过

        # 搜索项目简介
        try:
            profiles = client.get_collection("project_profiles")
            if profiles.count() > 0:
                results = profiles.query(query_texts=[query], n_results=1)
                if results and results["documents"] and results["documents"][0]:
                    parts.insert(0, f"--- 项目简介 ---\n{results['documents'][0][0]}")
        except Exception:
            pass

        context = "\n".join(parts)
        if context:
            print(f"--- [P34] ✅ Chroma Cloud 项目上下文: {len(context)} 字, {len(parts)} 条 ---")
        else:
            print("--- [P34] ⚠️ Chroma Cloud 无匹配数据 ---")
        return context

    except Exception as e:
        print(f"[binance_square] Chroma Cloud fetch failed: {e}")
        return ""


def _post_process(text: str) -> str:
    """统一后处理"""
    if not text:
        return text
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'——', '，', text)
    text = re.sub(r'—', '，', text)
    text = text.replace('；', '。')
    text = re.sub(r'^#+\s*.*\n', '', text, flags=re.MULTILINE)
    return text.strip()


def _generate_variant(
    raw_input: str,
    plan: dict,
    system_prompt_context: dict,
    length_constraints: dict,
    api_config: dict,
) -> str:
    """根据策略官方案生成单个版本"""
    label = plan.get("label", "")
    perspective = plan.get("perspective", "")
    story = plan.get("story", "")
    hook = plan.get("hook", "")
    detail = plan.get("detail", "")
    tone = plan.get("tone", "")
    logic_pattern = plan.get("logic_pattern", "")

    system_prompt = render_modular_prompt("writer/binance_square.jinja2", system_prompt_context)

    # P34 Phase 2: 获取项目上下文
    project_context = system_prompt_context.get("project_context", "")
    project_section = ""
    if project_context:
        project_section = f"\n\n📌 项目参考资料（以下为真实数据，必须基于此写作）：\n{project_context}"

    user_prompt = f"""素材：
{raw_input}{project_section}

你要写的版本：{label}
切入视角：{perspective}
这篇内容讲的故事：{story}
第一句的方向：{hook}
用这个事实/数据支撑：{detail}
语气：{tone}
写作公式：{logic_pattern}

⚠️ 严禁编造素材中没有的事实、数据、引言。只能使用上面提供的素材和参考资料。
⚠️ 这是币安广场帖子，保持专业教育向调性。
⚠️ 可以用 $TICKER 和 #话题标签。
⚠️ 结尾可以加互动提问或个人观点。
直接写。严格控制在{length_constraints['target']}字左右（{length_constraints['min']}-{length_constraints['max']}字）。"""

    provider = api_config.get("provider", "grok")
    api_key = api_config.get("api_key") or None
    model_id = api_config.get("model_id") or None
    max_tokens = min(int(length_constraints['target'] * 2), 2048)

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response_text = generate_text(
                prompt=user_prompt,
                api_key=api_key,
                model_id=model_id,
                provider=provider,
                temperature=0.8,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
            )
            return _post_process(response_text)
        except Exception as e:
            if attempt < max_retries and "Connection" in str(e):
                wait_time = 3 * (attempt + 1)
                print(f"--- [P34] ⚠️ {label} 第{attempt+1}次重试（{wait_time}s后）: {e} ---")
                time.sleep(wait_time)
            else:
                raise


def binance_square_writer(state: dict) -> dict:
    """
    币安广场 Writer - P34 3版本生成
    """
    raw_input = state["raw_input"]
    api_config = state.get("api_config", {})
    strategy_json = state.get("strategy_json", "{}")
    web3_knowledge = state.get("web3_knowledge", "")

    mode_config = get_mode_config("binance_square")
    length_constraints = mode_config.get("length", {"min": 100, "max": 900, "target": 500})

    custom_length = state.get("custom_length", 0)
    if custom_length and custom_length > 0:
        margin = int(custom_length * 0.2)
        length_constraints = {
            "min": max(100, custom_length - margin),
            "max": min(900, custom_length + margin),  # 币安广场硬限 900
            "target": custom_length
        }

    # P34: RAG 样本 (Chroma 语义匹配)
    rag_context = _get_rag_samples(query_text=raw_input)

    # P34: 声调锚定 (Chroma 最近帖子)
    voice_anchors = _get_voice_anchors(query_text=raw_input)

    # P34 Phase 2: Chroma Cloud 项目上下文
    project_context = _get_project_context(raw_input)

    shared_context = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "length": length_constraints,
        "raw_input": raw_input,
        "strategy_json": strategy_json,
        "web3_knowledge": web3_knowledge,
        "rag_context": rag_context,
        "voice_anchors": voice_anchors,
        "project_context": project_context,
        "forbidden_patterns": load_forbidden_patterns(),
    }

    # 从策略官输出提取方案
    print("--- [P34] 从策略官输出提取币安广场版本方案 ---")
    plans = _extract_plans(strategy_json)
    for i, p in enumerate(plans):
        print(f"  版本{i+1}: {p.get('label','')} | 视角: {p.get('perspective','')} | 公式: {p.get('logic_pattern','')}")

    # 按方案循环生成版本
    variants = []
    for i, plan in enumerate(plans):
        try:
            print(f"--- [P34] 写手生成广场版本 {i+1}/3: {plan.get('label','')} ({plan.get('tone','')}) ---")
            content = _generate_variant(
                raw_input=raw_input,
                plan=plan,
                system_prompt_context=shared_context,
                length_constraints=length_constraints,
                api_config=api_config,
            )
            variants.append({
                "key": f"variant_{i+1}",
                "label": plan.get("label", f"版本{i+1}"),
                "methods": [],
                "instruction": plan.get("story", ""),
                "content": content,
                "char_count": len(content) if content else 0,
            })
        except Exception as e:
            print(f"--- [P34] ❌ 版本 {i+1} 失败: {e} ---")
            variants.append({
                "key": f"variant_{i+1}",
                "label": plan.get("label", f"版本{i+1}"),
                "methods": [],
                "instruction": plan.get("angle", ""),
                "content": f"[生成失败: {e}]",
                "char_count": 0,
            })

    first_content = next((v["content"] for v in variants if v["char_count"] > 0), "")

    # P34: 自动存入 Chroma (去重 + 声调库)
    try:
        from app.services.chroma_service import get_chroma_service
        chroma = get_chroma_service()
        for v in variants:
            if v["char_count"] > 0:
                content_id = f"bs_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{v['key']}"
                chroma.add_content_history(
                    content_id=content_id,
                    content=v["content"],
                    metadata={"platform": "binance_square", "date": datetime.now().isoformat()},
                )
                chroma.add_published_post(
                    post_id=content_id,
                    content=v["content"],
                    metadata={"platform": "binance_square", "date": datetime.now().isoformat()},
                )
    except Exception as e:
        print(f"[binance_square] Chroma save failed (non-critical): {e}")

    return {
        "draft_content": first_content,
        "variants": variants,
    }
