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
from .core.lark_client import lark_client
from .api.cleaner import router as cleaner_router
import os

app = FastAPI(title="Web3 Consensus Engine API", version="5.0")

# Register routers
app.include_router(cleaner_router)

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

class GenerateRequest(BaseModel):
    input: str
    mode: str
    narrative_type: str = "project_review"
    references: List[str] = [] 
    selected_option: Optional[Dict[str, Any]] = None # P4: 用户选择的选题方案
    info_anchors: Optional[Any] = None # P4: Global context from analysis (List or Dict)
    api_config: APIConfig = APIConfig()
    agent_config: Optional[Dict[str, APIConfig]] = None 

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
                "narrative_type": request.narrative_type,
                "references": request.references,
                "api_config": request.api_config.dict(),
                "agent_config": agent_config_dict,
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

        inputs = {
            "raw_input": request.input, 
            "mode": request.mode, 
            "narrative_type": request.narrative_type,
            "references": request.references,
            "selected_option": request.selected_option, # Pass selected option
            "info_anchors": request.info_anchors, # Pass global context
            "api_config": request.api_config.dict(),
            "agent_config": agent_config_dict,
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

