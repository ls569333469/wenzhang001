from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List # Added List
from .graph import app_graph, node_strategist # Import node_strategist for analyze
import asyncio
from fastapi.responses import StreamingResponse
import json
from .core.config import ensure_config_dir, load_config, save_config
from .core.mode_configs import get_mode_config, MODE_CONFIGS  # P14: 模式配置
from .core.lark_client import lark_client
from .api.cleaner import router as cleaner_router
from .api.materials import router as materials_router
from .api.creations import router as creations_router
import os
from pathlib import Path

app = FastAPI(title="Web3 Consensus Engine API", version="5.0")

@app.get("/api/web2-authors")
async def get_web2_authors():
    """获取 Web2 风格目录下的所有博主"""
    web2_dir = Path(__file__).parent.parent / "data" / "Web2风格"
    if not web2_dir.exists():
        return {"authors": []}
    # 过滤隐藏文件夹
    authors = [d.name for d in web2_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    return {"authors": sorted(authors)}

# Register routers
app.include_router(cleaner_router)
app.include_router(materials_router)
app.include_router(creations_router)

@app.on_event("startup")
async def startup_event():
    ensure_config_dir()
    # Start background sync task
    asyncio.create_task(background_sync_task())

async def background_sync_task():
    """Run sync every 10 minutes"""
    from .services.sync_service import sync_service
    from .core.config import get_logger
    logger = get_logger("scheduler")
    
    while True:
        try:
            logger.info("Scheduler: Starting scheduled Lark sync...")
            result = sync_service.sync_from_lark()
            logger.info(f"Scheduler: Sync completed. {result}")
        except Exception as e:
            logger.error(f"Scheduler: Sync failed: {e}")
        
        # Wait 10 minutes (600 seconds)
        await asyncio.sleep(600)

@app.post("/config/lark-sync")
async def trigger_sync():
    """Manual trigger for Lark Sync"""
    from .services.sync_service import sync_service
    try:
        result = sync_service.sync_from_lark()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class APIConfig(BaseModel):
    api_key: str = ""
    model_id: str = ""
    provider: str = "volcengine"

class CustomPrompts(BaseModel):
    writer: Optional[str] = None
    strategist: Optional[str] = None
    critic: Optional[str] = None
    polisher: Optional[str] = None

class GenerateRequest(BaseModel):
    input: str
    mode: str = "mid_article"  # P16: 创作模式 (hot_take, mid_article, long_article, tutorial)
    style: str = "auto"  # P10: 写作风格 (auto, mimeng, banfo, xinshixiang, insider)
    length_type: str = "auto"  # P16: 篇幅类型 (auto=用模式默认, custom=自定义字数)
    custom_length: Optional[int] = None  # P16: 自定义字数 (50-5000)
    retention_level: int = 3  # P10: 保留度等级 1-5 (1=95%保留, 5=10%保留)
    narrative_type: str = "project_review"
    references: List[str] = [] 
    selected_option: Optional[Dict[str, Any]] = None # P4: 用户选择的选题方案
    info_anchors: Optional[Any] = None # P4: Global context from analysis (List or Dict)
    api_config: APIConfig = APIConfig()
    agent_config: Optional[Dict[str, APIConfig]] = None
    custom_prompts: Optional[CustomPrompts] = None  # P15: 自定义提示词 
    material_context: Optional[str] = None  # P23: 素材原文参考

@app.post("/analyze")
async def analyze_narrative(request: GenerateRequest):
    """
    P4/P5: Executes Strategist node with streaming feedback via SSE.
    """
    async def event_generator():
        try:
            # 准备 config
            agent_config_dict = {}
            if request.agent_config:
                agent_config_dict = {k: v.dict() for k, v in request.agent_config.items()}

            inputs = {
                "raw_input": request.input, 
                "mode": request.mode,
                "style": request.style,  # P10
                "length": request.length,  # P10
                "custom_length": request.custom_length or 0,  # P16: 自定义字数
                "retention_level": request.retention_level,  # P10
                "narrative_type": request.narrative_type,
                "references": request.references,
                "api_config": request.api_config.dict(),
                "agent_config": agent_config_dict,
                "custom_prompts": request.custom_prompts.dict() if request.custom_prompts else {},  # P15
                "material_context": request.material_context or "",  # P23: 素材原文
            }
            
            # --- Step 1: Context & Style Loading ---
            yield f"data: {json.dumps({'type': 'thinking_step', 'agent': 'strategist', 'step': 'init', 'detail': 'Initializing analysis context...'})}\n\n"
            await asyncio.sleep(0.1)
            
            from .agents.strategist import build_strategist_context, build_strategist_prompt, execute_strategist_analysis
            
            yield f"data: {json.dumps({'type': 'thinking_step', 'agent': 'strategist', 'step': 'context', 'detail': f'Loading style samples for mode: {request.mode}'})}\n\n"
            context = build_strategist_context(inputs)
            await asyncio.sleep(0.3) # User friendly delay
            
            # --- Step 2: Prompt Construction ---
            ref_count = len(request.references)
            yield f"data: {json.dumps({'type': 'thinking_step', 'agent': 'strategist', 'step': 'analysis', 'detail': f'Analyzing input with {ref_count} reference(s)...'})}\n\n"
            system_prompt, user_prompt = build_strategist_prompt(context, inputs)
            await asyncio.sleep(0.3)

            # --- Step 3: LLM Execution ---
            # Get effective config for display
            global_config = inputs.get('api_config', {})
            specific_config = inputs.get('agent_config', {}).get('strategist', {})
            effective_config = specific_config if specific_config.get("provider") else global_config
            provider_name = effective_config.get("provider", "unknown")
            
            yield f"data: {json.dumps({'type': 'thinking_step', 'agent': 'strategist', 'step': 'query', 'detail': f'Querying {provider_name} reasoning model...'})}\n\n"
            
            # Execute (Blocking LLM call, but we have already sent status)
            # In a real async system we might use loop.run_in_executor if this was very slow blocking IO, 
            # but generate_text is synchronous.
            strategy_json_str = execute_strategist_analysis(user_prompt, system_prompt, effective_config)
            
            # --- Step 4: Parsing & Result ---
            yield f"data: {json.dumps({'type': 'thinking_step', 'agent': 'strategist', 'step': 'parsing', 'detail': 'Parsing strategy options...'})}\n\n"
            
            try:
                strategy_data = json.loads(strategy_json_str)
                
                # P20: 诊断日志 - 检查 context_card
                from .core.config import get_logger
                p20_logger = get_logger("strategist")
                if "context_card" in strategy_data:
                    p20_logger.info(f"[P20] ✅ context_card 已生成: {strategy_data['context_card']}")
                else:
                    p20_logger.warning("[P20] ⚠️ Strategist 未返回 context_card 字段")
                
                # P25: 短篇策略官输出 plans 而非 options
                # 不需要用户选择，直接标记 auto_proceed 让前端自动继续
                if "plans" in strategy_data and "options" not in strategy_data:
                    strategy_data["auto_proceed"] = True
                    p20_logger.info(f"[P25] ✅ 短篇模式 auto_proceed: {len(strategy_data['plans'])} 个 plans")
                
                # Send the final result as a distinct event type
                yield f"data: {json.dumps({'type': 'analysis_result', 'payload': strategy_data})}\n\n"
                
                yield f"data: {json.dumps({'type': 'agent_update', 'step': 'strategist', 'status': 'completed', 'logs': ['分析已成功完成。']})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'JSON Parse Error: {str(e)}'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        # End stream
        yield f"data: {json.dumps({'type': 'end', 'payload': '分析完成'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/generate")
async def generate_narrative(request: GenerateRequest):
    """
    Executes the agent workflow and streams updates via SSE.
    """
    async def event_generator():
        agent_config_dict = {}
        if request.agent_config:
            agent_config_dict = {k: v.dict() for k, v in request.agent_config.items()}

        # P16.1: 移除旧的 enforce_mode_length，字数约束现在由 mode_configs 在 Writer/Critic 中处理
        
        inputs = {
            "raw_input": request.input, 
            "mode": request.mode,
            "style": request.style,  # P10
            "custom_length": request.custom_length or 0,  # P16: 自定义字数
            "retention_level": request.retention_level,  # P10
            "narrative_type": request.narrative_type,
            "references": request.references,
            "selected_option": request.selected_option, # Pass selected option
            "info_anchors": request.info_anchors, # Pass global context
            "api_config": request.api_config.dict(),
            "agent_config": agent_config_dict,
            "custom_prompts": request.custom_prompts.dict() if request.custom_prompts else {},  # P15
            "revision_count": 0,
            "thinking_steps": []
        }
        
        try:
            generated_text = ""

            async for output in app_graph.astream(inputs):
                for node_name, node_state in output.items():
                    # 提取思考步骤
                    thinking_steps = node_state.get("thinking_steps", [])
                    
                    # 推送每个思考步骤
                    for step_group in thinking_steps:
                        agent = step_group.get("agent", node_name)
                        steps = step_group.get("steps", [])
                        
                        for i, step in enumerate(steps):
                            step_data = {
                                "type": "thinking_step",
                                "agent": agent,
                                "step": step["step"], 
                                "detail": step.get("content", ""),
                                "progress": (i + 1) / len(steps) * 100 if steps else 100
                            }
                            yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"
                            await asyncio.sleep(0.3)
                    
                    # 推送 Agent 完成状态
                    status_data = {
                        "type": "agent_update",
                        "step": node_name,
                        "status": "completed",
                        "logs": node_state.get("logs", [])
                    }
                    yield f"data: {json.dumps(status_data, ensure_ascii=False)}\n\n"
                    
                    # P19: 在 writer 节点完成后，立即推送 draft_v1 作为预览内容
                    # 这样用户可以在 critique/polish 阶段就看到内容
                    if "draft_v1" in node_state and node_state["draft_v1"]:
                        draft_preview = node_state["draft_v1"]
                        preview_data = {
                            "type": "content_preview",  # 区分于 final_result
                            "payload": draft_preview
                        }
                        yield f"data: {json.dumps(preview_data, ensure_ascii=False)}\n\n"
                    
                    # 如果有最终内容，推送它
                    if "final_content" in node_state and node_state["final_content"]:
                        generated_text = node_state["final_content"]
                        content_data = {
                            "type": "final_result",
                            "payload": generated_text
                        }
                        yield f"data: {json.dumps(content_data, ensure_ascii=False)}\n\n"
                
                await asyncio.sleep(0.2)
            
            # --- P10: Auto-Archive to Lark ---
            if generated_text:
                try:
                    ensure_config_dir()
                    lark_base_token = os.getenv("LARK_BASE_TOKEN")
                    lark_table_id = os.getenv("LARK_TABLE_ID")
                    
                    if lark_base_token and lark_table_id:
                        yield f"data: {json.dumps({'type': 'thinking_step', 'agent': 'system', 'step': 'archiving', 'detail': 'Archiving to Lark Base...'})}\n\n"
                        
                        archive_fields = {
                            "内容": request.input[:1000] + "..." if len(request.input) > 1000 else request.input, # Limited length
                            "AI生成结果": generated_text,
                            "状态": "已完成",
                            "风格": request.mode,
                            "类型": request.narrative_type
                        }
                        
                        lark_client.create_record(lark_base_token, lark_table_id, archive_fields)
                        yield f"data: {json.dumps({'type': 'agent_update', 'step': 'system', 'status': 'completed', 'logs': ['✅ Successfully archived to Lark Base']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'agent_update', 'step': 'system', 'status': 'completed', 'logs': ['⚠️ Lark Token not set, skipping archive']})}\n\n"
                        
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'agent_update', 'step': 'system', 'status': 'failed', 'logs': [f'❌ Archive Failed: {str(e)}']})}\n\n"

            yield f"data: {json.dumps({'type': 'end', 'payload': 'Process Finished'})}\n\n"
        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ============================================
# P14: Hot Take 独立 API (锐评模式)
# ============================================
class HotTakeRequest(BaseModel):
    input: str
    api_config: APIConfig = APIConfig()
    custom_prompts: Optional[CustomPrompts] = None

@app.post("/hot_take", deprecated=True)
async def generate_hot_take(request: HotTakeRequest):
    """
    P14: 锐评模式独立API - 不走LangGraph，直接生成3条候选
    @deprecated P27: 锐评已迁入标准 LangGraph 管线，此端点保留兼容
    """
    from .core.llm import generate_text  # 修复: 使用正确的函数名
    from datetime import datetime
    from jinja2 import Environment, FileSystemLoader
    
    try:
        # 获取模式配置
        config = get_mode_config("hot_take")
        
        # 加载 hot_take.jinja2 模板
        prompts_dir = Path(__file__).parent.parent / "data" / "prompts" / "writer"
        env = Environment(loader=FileSystemLoader(str(prompts_dir)))
        
        if request.custom_prompts and request.custom_prompts.writer:
            # P15: 使用自定义提示词
            template = env.from_string(request.custom_prompts.writer)
        else:
            # 使用默认文件模板
            template = env.get_template("hot_take.jinja2")
        
        # 渲染模板
        system_prompt = template.render(
            current_time_str=datetime.now().strftime("%Y-%m-%d %H:%M"),
            raw_input=request.input
        )
        
        # 调用 LLM (使用 generate_text)
        response = generate_text(
            prompt="请根据系统提示生成锐评候选，输出JSON格式。",
            api_key=request.api_config.api_key or None,
            model_id=request.api_config.model_id or None,
            provider=request.api_config.provider,
            temperature=0.8,
            system_prompt=system_prompt
        )
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"candidates": [{"id": 1, "content": response, "word_count": len(response)}]}
        except json.JSONDecodeError:
            result = {"candidates": [{"id": 1, "content": response, "word_count": len(response)}]}
        
        return {
            "status": "success",
            "mode": "hot_take",
            "config": {
                "length": config["length"],
                "output_count": config["output_count"]
            },
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hot Take 生成失败: {str(e)}")


@app.get("/health")
async def health_check():
    # Check Lark connection status
    lark_connected = False
    try:
        # Test Lark connection by checking if client has valid token
        if lark_client and hasattr(lark_client, 'tenant_access_token'):
            lark_connected = lark_client.tenant_access_token is not None
    except Exception:
        lark_connected = False
    
    return {
        "status": "ok", 
        "version": "6.2", 
        "engine": "Web3 Consensus Engine",
        "lark_connected": lark_connected
    }

@app.get("/config/styles")
async def get_styles():
    """返回可用的风格配置"""
    from .styles import get_style_loader
    loader = get_style_loader()
    styles = [{"id": s.id, "name": s.name, "icon": s.icon, "color": s.color, "description": s.description} 
              for s in loader.get_all_styles()]
    combinations = [{"id": c.id, "name": c.name, "description": c.description, "styles": c.styles}
                    for c in loader.get_all_combinations()]
    return {"styles": styles, "combinations": combinations}

@app.get("/config/models")
async def get_models():
    """返回各 LLM 提供商的可用模型列表"""
    from .core.llm import PROVIDER_CONFIGS
    
    result = {}
    for provider, config in PROVIDER_CONFIGS.items():
        result[provider] = {
            "default_model": config.get("default_model", ""),
            "available_models": config.get("available_models", [config.get("default_model", "")])
        }
    return result

class PromptUpdateRequest(BaseModel):
    content: str

@app.get("/config/prompts")
async def get_prompts():
    """获取所有 Agent 的当前 Prompt 模板"""
    from .core.prompts import load_template
    agents = ["strategist", "writer", "critic", "polisher"]
    return {agent: load_template(agent) for agent in agents}

@app.post("/config/prompts/{agent_name}")
async def update_prompt(agent_name: str, request: PromptUpdateRequest):
    """更新指定 Agent 的 Prompt 模板"""
    from .core.prompts import save_template
    try:
        save_template(agent_name, request.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class APIKeysRequest(BaseModel):
    gemini: Optional[str] = ""
    deepseek: Optional[str] = ""
    doubao: Optional[str] = ""
    openai: Optional[str] = ""
    claude: Optional[str] = ""

@app.get("/config/keys")
async def get_api_keys():
    """Get configured API keys (masked)."""
    config = load_config()
    keys = config.get("api_keys", {})
    
    # Mask keys for security
    masked_keys = {}
    for k, v in keys.items():
        if v and len(v) > 8:
            masked_keys[k] = v[:4] + "***" + v[-4:]
        elif v:
            masked_keys[k] = "***"
        else:
            masked_keys[k] = ""
            
    return masked_keys

@app.post("/config/keys")
async def save_api_keys(keys: APIKeysRequest):
    """Save API keys to configuration file."""
    config = load_config()
    current_keys = config.get("api_keys", {})
    
    # Update keys
    new_keys = keys.dict()
    for k, v in new_keys.items():
        if v: # Only update if value provided
            current_keys[k] = v
            
    config["api_keys"] = current_keys
    save_config(config)
    return {"status": "success"}

@app.get("/config/lark-status")
async def get_lark_status():
    """Get Lark Sync Status (Count & Last Sync Time)"""
    from .services.sync_service import sync_service, STYLE_LIBRARY_FILE
    import os
    from datetime import datetime
    
    library = sync_service.load_library()
    count = len(library)
    last_sync = "Never"
    
    if STYLE_LIBRARY_FILE.exists():
        mtime = os.path.getmtime(STYLE_LIBRARY_FILE)
        last_sync = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        
    return {
        "status": "active" if count > 0 else "empty",
        "count": count,
        "last_sync": last_sync
    }


# ============================================
# Feature Flags API (P12)
# ============================================

class FeatureFlagsRequest(BaseModel):
    use_knowledge_repo: Optional[bool] = None


@app.get("/config/feature-flags")
async def get_feature_flags():
    """获取 Feature Flags 配置"""
    config = load_config()
    flags = config.get("feature_flags", {})
    return {
        "use_knowledge_repo": flags.get("use_knowledge_repo", False)
    }


@app.post("/config/feature-flags")
async def save_feature_flags(flags: FeatureFlagsRequest):
    """保存 Feature Flags 配置"""
    config = load_config()
    if "feature_flags" not in config:
        config["feature_flags"] = {}
    
    # 只更新提供的 flags
    flags_dict = flags.dict(exclude_none=True)
    for k, v in flags_dict.items():
        config["feature_flags"][k] = v
    
    save_config(config)
    return {"status": "success", "updated": flags_dict}


# ============================================
# P27-P2: DataPanel 数据 API
# ============================================

from app.services.data_service import data_service

@app.get("/api/data/bullish")
async def get_bullish_feed(category: Optional[str] = None, limit: int = 20):
    """🌸 吹捧素材 Feed (Tab: 吹捧素材)"""
    try:
        items = data_service.get_bullish_feed(category=category, limit=limit)
        return {"items": items, "total": len(items)}
    except Exception as e:
        logger.error(f"[DataAPI] bullish feed error: {e}")
        return {"items": [], "total": 0, "error": str(e)}


@app.get("/api/data/kaito/projects")
async def get_kaito_projects():
    """🎯 嘴撸项目列表 (Tab: 嘴撸项目)"""
    try:
        projects = data_service.get_kaito_projects()
        return {"projects": projects}
    except Exception as e:
        logger.error(f"[DataAPI] kaito projects error: {e}")
        return {"projects": [], "error": str(e)}


@app.get("/api/data/kaito/{project_id}/intel")
async def get_kaito_intel(project_id: str):
    """🎯 某项目角度+情报 (Tab: 嘴撸_{项目名})"""
    try:
        intel = data_service.get_kaito_intel(project_id=project_id)
        return intel
    except Exception as e:
        logger.error(f"[DataAPI] kaito intel error: {e}")
        return {"project": project_id, "angles": [], "news": [], "error": str(e)}


@app.get("/api/data/research")
async def get_research_projects(q: Optional[str] = None):
    """🔬 搜索投研项目 (Tab: 投研项目)"""
    try:
        projects = data_service.get_research_projects(query=q)
        return {"projects": projects, "total": len(projects)}
    except Exception as e:
        logger.error(f"[DataAPI] research error: {e}")
        return {"projects": [], "total": 0, "error": str(e)}


# ============================================
# Ingest Management API (P13)
# ============================================

@app.get("/ingest/status")
async def get_ingest_status():
    """获取入库状态 (Hash 缓存和 Lark 记录数)"""
    import sys
    from pathlib import Path
    
    # 动态导入 hash_cache (避免启动时依赖)
    scripts_path = Path(__file__).parent.parent / "scripts"
    if str(scripts_path) not in sys.path:
        sys.path.insert(0, str(scripts_path))
    
    hash_count = 0
    try:
        from batch.hash_cache import get_hash_cache
        hash_cache = get_hash_cache()
        hash_count = len(hash_cache)
    except Exception as e:
        print(f"[Ingest API] Hash cache error: {e}")
    
    # 获取 Lark 表记录数
    lark_count = 0
    try:
        base_token = os.getenv("LARK_BASE_TOKEN")
        table_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
        if base_token and table_id:
            resp = lark_client.list_records(base_token, table_id, page_size=1)
            lark_count = resp.get("data", {}).get("total", 0)
    except Exception as e:
        print(f"[Ingest API] Lark count error: {e}")
    
    return {
        "hash_cache_count": hash_count,
        "lark_record_count": lark_count,
        "status": "ready"
    }


@app.post("/ingest/cache/clear")
async def clear_ingest_cache():
    """清空 Hash 缓存"""
    import sys
    from pathlib import Path
    
    scripts_path = Path(__file__).parent.parent / "scripts"
    if str(scripts_path) not in sys.path:
        sys.path.insert(0, str(scripts_path))
    
    try:
        from batch.hash_cache import get_hash_cache
        cache = get_hash_cache()
        cache.clear()
        return {"status": "success", "message": "Hash 缓存已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ingest/folders")
async def get_ingest_folders(source: str = "web3"):
    """获取所有文件夹及其状态 (已入库/总数)"""
    from pathlib import Path
    import sys
    import json
    import hashlib
    
    # 动态导入 hash_cache
    scripts_path = Path(__file__).parent.parent / "scripts"
    if str(scripts_path) not in sys.path:
        sys.path.insert(0, str(scripts_path))
    
    try:
        from batch.hash_cache import get_hash_cache
        hash_cache = get_hash_cache()
    except Exception:
        hash_cache = set()
    
    # 根据 source 选择数据目录
    if source == "web2":
        data_dir = Path(__file__).parent.parent / "data" / "Web2风格"
        file_pattern = "*.txt"  # Web2 使用 TXT 文件
    else:
        data_dir = Path(__file__).parent.parent / "data" / "Web3素材"
        file_pattern = "*.json"
    
    folders = []
    total_processed = 0
    total_pending = 0
    
    if data_dir.exists():
        for folder in sorted(data_dir.iterdir()):
            if folder.is_dir():
                files = list(folder.glob(file_pattern))
                total_count = len(files)
                processed_count = 0
                
                # 遍历每个文件检查是否在 hash_cache 中
                for file in files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            if file.suffix == '.json':
                                data = json.load(f)
                                content = data.get('content', '')
                            else:
                                content = f.read()
                        h = hashlib.md5(content.encode()).hexdigest()
                        if h in hash_cache:
                            processed_count += 1
                    except Exception:
                        pass
                
                pending_count = total_count - processed_count
                total_processed += processed_count
                total_pending += pending_count
                
                # 判断状态
                if total_count == 0:
                    status = "empty"
                elif processed_count == total_count:
                    status = "completed"
                elif processed_count > 0:
                    status = "partial"
                else:
                    status = "pending"
                
                folders.append({
                    "name": folder.name,
                    "total_count": total_count,
                    "processed_count": processed_count,
                    "pending_count": pending_count,
                    "status": status
                })
    
    return {
        "folders": folders, 
        "total": len(folders),
        "total_processed": total_processed,
        "total_pending": total_pending
    }


class IngestStartRequest(BaseModel):
    mode: str = "optimized"  # optimized | legacy
    source: str = "web3"     # web3 | web2 | custom
    custom_path: Optional[str] = None  # 自定义目录路径
    target_table: str = "web3"  # web3 | web2 目标表格
    # Web2 专用参数
    web2_author: Optional[str] = None  # 博主名称
    web2_style: Optional[str] = None   # 风格标签


@app.post("/ingest/start")
async def start_ingest(request: IngestStartRequest):
    """启动入库任务 (后台运行)"""
    import subprocess
    from pathlib import Path
    from datetime import datetime
    
    backend_dir = Path(__file__).parent.parent
    
    # 创建日志目录
    log_dir = backend_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 选择脚本
    if request.mode == "optimized":
        script = "scripts.ingest_optimized"
    else:
        script = "scripts.ingest_knowledge"
    
    # 构建命令
    cmd = [
        str(backend_dir / "venv" / "Scripts" / "python.exe"),
        "-m", script,
    ]
    
    # 根据数据源添加参数
    if request.source == "custom" and request.custom_path:
        # 自定义目录
        cmd.extend(["--path", request.custom_path])
        cmd.extend(["--target", request.target_table])
        # Web2 专用参数
        if request.target_table == "web2":
            if request.web2_author:
                cmd.extend(["--author", request.web2_author])
            if request.web2_style:
                cmd.extend(["--style", request.web2_style])
    elif request.source == "web2" and request.custom_path:
        # Web2 数据源 + 自定义路径
        cmd.extend(["--path", request.custom_path])
        cmd.extend(["--target", "web2"])
        if request.web2_author:
            cmd.extend(["--author", request.web2_author])
        if request.web2_style:
            cmd.extend(["--style", request.web2_style])
    else:
        # 使用默认目录
        cmd.append("--all")
    
    try:
        # 使用 subprocess.Popen 在后台运行，输出到日志文件
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== 入库任务启动 ===\n")
            f.write(f"时间: {datetime.now().isoformat()}\n")
            f.write(f"命令: {' '.join(cmd)}\n")
            f.write(f"模式: {request.mode}\n")
            f.write(f"数据源: {request.source}\n")
            if request.custom_path:
                f.write(f"自定义路径: {request.custom_path}\n")
            f.write(f"===================\n\n")
        
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=open(log_file, 'a', encoding='utf-8'),
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        # 记录到历史
        config = load_config()
        if "ingest_history" not in config:
            config["ingest_history"] = []
        config["ingest_history"].append({
            "timestamp": datetime.now().isoformat(),
            "pid": process.pid,
            "source": request.source,
            "custom_path": request.custom_path,
            "log_file": str(log_file),
            "status": "running"
        })
        save_config(config)
        
        return {
            "status": "started",
            "pid": process.pid,
            "script": script,
            "log_file": str(log_file),
            "message": f"入库任务已启动 (PID: {process.pid})"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/pause")
async def pause_ingest():
    """暂停入库任务 (占位符)"""
    # 实际暂停需要更复杂的进程管理，这里仅返回成功
    return {"status": "paused", "message": "暂停功能待实现"}


# ============================================
# P2: Ingest Configuration API
# ============================================

class IngestConfigRequest(BaseModel):
    data_source: str = "web3"  # web3 | web2
    custom_path: Optional[str] = None


@app.get("/ingest/config")
async def get_ingest_config():
    """获取入库配置"""
    config = load_config()
    ingest_config = config.get("ingest_config", {})
    return {
        "data_source": ingest_config.get("data_source", "web3"),
        "custom_path": ingest_config.get("custom_path", None),
        "available_sources": [
            {"id": "web3", "name": "Web3素材", "path": "data/Web3素材", "enabled": True},
            {"id": "web2", "name": "Web2风格", "path": "data/Web2风格", "enabled": True}
        ]
    }


@app.post("/ingest/config")
async def save_ingest_config(request: IngestConfigRequest):
    """保存入库配置"""
    config = load_config()
    if "ingest_config" not in config:
        config["ingest_config"] = {}
    
    config["ingest_config"]["data_source"] = request.data_source
    if request.custom_path:
        config["ingest_config"]["custom_path"] = request.custom_path
    
    save_config(config)
    return {"status": "success", "updated": config["ingest_config"]}


# ============================================
# P3: Ingest History API
# ============================================

@app.get("/ingest/history")
async def get_ingest_history():
    """获取入库历史记录"""
    config = load_config()
    history = config.get("ingest_history", [])
    return {"history": history[-10:]}  # 返回最近 10 条


@app.post("/ingest/history")
async def add_ingest_history():
    """添加入库历史记录 (由入库脚本调用)"""
    from datetime import datetime
    
    config = load_config()
    if "ingest_history" not in config:
        config["ingest_history"] = []
    
    config["ingest_history"].append({
        "timestamp": datetime.now().isoformat(),
        "status": "started"
    })
    
    save_config(config)
    return {"status": "success"}


# ============================================
# P5: Directory Browse API
# ============================================

@app.get("/ingest/browse")
async def browse_directory(path: str = ""):
    """浏览任意本地目录"""
    from pathlib import Path
    
    # 默认从 D 盘开始（可配置）
    if not path:
        # 尝试 D 盘，如果不存在则用 C 盘
        if Path("D:/").exists():
            target_path = Path("D:/")
        else:
            target_path = Path("C:/")
    else:
        target_path = Path(path)
    
    if not target_path.exists() or not target_path.is_dir():
        return {"items": [], "current_path": str(target_path), "parent_path": None, "error": "目录不存在"}
    
    items = []
    files = []
    try:
        for item in sorted(target_path.iterdir()):
            # 跳过系统隐藏项
            if item.name.startswith('$') or item.name.startswith('.'):
                continue
            
            if item.is_dir():
                try:
                    children_count = len(list(item.iterdir()))
                except (PermissionError, OSError):
                    children_count = 0
                
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": True,
                    "children_count": children_count
                })
            else:
                # 返回文件信息
                try:
                    size = item.stat().st_size
                except Exception:
                    size = 0
                
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": False,
                    "size": size,
                    "ext": item.suffix.lower()
                })
    except PermissionError:
        return {"items": [], "current_path": str(target_path), "parent_path": str(target_path.parent), "error": "无访问权限"}
    
    # 返回上级（根目录除外）
    parent_path = None
    if target_path.parent != target_path:  # 不是根目录
        parent_path = str(target_path.parent)
    
    return {
        "items": items,
        "files": files,
        "current_path": str(target_path),
        "parent_path": parent_path
    }


# ============================================
# 配置管理 API
# ============================================

@app.get("/config/ingest")
async def get_ingest_config():
    """获取数据清洗配置"""
    import os
    return {
        "web3_table_id": os.getenv("LARK_KNOWLEDGE_TABLE_ID", ""),
        "web2_table_id": os.getenv("LARK_WEB2_TABLE_ID", "") or os.getenv("LARK_TABLE_ID", ""),
        "score_threshold": 6  # 默认阈值
    }


class IngestConfigRequest(BaseModel):
    web3_table_id: Optional[str] = None
    web2_table_id: Optional[str] = None
    score_threshold: int = 6


@app.put("/config/ingest")
async def update_ingest_config(config: IngestConfigRequest):
    """更新数据清洗配置 (保存到 .env 文件)"""
    from pathlib import Path
    
    env_path = Path(__file__).parent.parent / ".env"
    
    try:
        # 读取现有 .env 内容
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # 更新或添加配置
        updated = {}
        if config.web3_table_id:
            updated["LARK_KNOWLEDGE_TABLE_ID"] = config.web3_table_id
        if config.web2_table_id:
            updated["LARK_WEB2_TABLE_ID"] = config.web2_table_id
        
        # 更新行
        new_lines = []
        for line in lines:
            key = line.split("=")[0].strip() if "=" in line else ""
            if key in updated:
                new_lines.append(f"{key}={updated[key]}\n")
                del updated[key]
            else:
                new_lines.append(line)
        
        # 添加新的配置
        for key, value in updated.items():
            new_lines.append(f"{key}={value}\n")
        
        # 写回 .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return {"status": "success", "message": "配置已保存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
