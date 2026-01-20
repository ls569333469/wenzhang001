from typing import TypedDict, Annotated, List, Union, Dict, Any
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime
import json

# 定义状态字典
class AgentState(TypedDict):
    raw_input: str
    mode: str  # "mimeng", "diary", "insider"
    narrative_type: str  # 新增：叙事类型
    references: List[str]  # P3: 选题参考列表
    selected_option: Dict[str, Any] # P4: 用户选择的选题方案
    api_config: Dict[str, Any]  # 默认/全局 API 配置
    agent_config: Dict[str, Dict[str, Any]]  # 新增：每个 Agent 的特定配置
    strategy_plan: str
    strategy_json: str  # 新增：策略 JSON（用于传递给 writer）
    info_anchors: Dict[str, Any]  # 信息锚点
    draft_v1: str
    critique_feedback: str
    critique_score: int
    final_content: str
    revision_count: int
    logs: Annotated[List[str], operator.add]
    thinking_steps: Annotated[List[Dict[str, Any]], operator.add]  # 思考步骤

# 1. 策略官节点
def node_strategist(state: AgentState):
    from .agents.strategist import strategist_agent
    print("--- [Step 1] Strategist is Thinking ---")
    
    steps = []
    
    # Check if option is already selected
    if state.get("selected_option"):
        print("--- [Step 1] Using Selected Option (Skipping LLM) ---")
        option = state["selected_option"]
        steps.append({"step": "config", "content": "使用用户选择的选题方案"})
        
        # Construct plan data from selected option
        # We start with the option data
        plan_data = option.copy()
        
        # Inject info_anchors from state if available (passed from frontend -> main -> state)
        if state.get("info_anchors"):
            plan_data["info_anchors"] = state["info_anchors"]
        
        # We need to serialize it back to string for Writer (who expects strategy_plan string or json)
        plan_json = json.dumps(plan_data, ensure_ascii=False)
        
        steps.append({"step": "identified", "content": f"识别痛点: {plan_data.get('pain_point', '已选定')}"})
        steps.append({"step": "angle", "content": f"切入角度: {plan_data.get('hook_angle', '已选定')}"})
        steps.append({"step": "outline", "content": f"加载大纲: {len(plan_data.get('outline', []))} 个要点"})
        steps.append({"step": "completed", "content": "策略规划加载完成"})
        
        return {
            "strategy_plan": plan_json,
            "strategy_json": plan_json,
            "logs": [f"[{datetime.now().isoformat()}] Strategist used selected option."],
            "thinking_steps": [{"agent": "strategist", "steps": steps, "status": "completed"}]
        }

    # Normal Flow (LLM Generation)
    print(f"--- Using narrative_type: {state.get('narrative_type', 'default')} ---")
    print(f"--- API Config: {state.get('api_config', {})} ---")
    
    # 获取配置
    global_config = state.get('api_config', {})
    specific_config = state.get('agent_config', {}).get('strategist', {})
    effective_config = specific_config if specific_config.get("provider") else global_config
    
    print(f"--- [Step 1] Strategist Config: {effective_config.get('provider')} ---")
    
    steps.append({"step": "analyzing", "content": f"正在分析输入素材 ({len(state['raw_input'])} 字)..."})
    steps.append({"step": "config", "content": f"叙事类型: {state.get('narrative_type', 'project_review')}"})
    
    # 构建特定的 agent state 进行传递
    agent_state = state.copy()
    agent_state['api_config'] = effective_config
    
    # 传递 state 给 agent
    try:
        plan = strategist_agent(agent_state)
    except Exception as e:
         steps.append({"step": "error", "content": f"Strategist Error: {str(e)}"})
         plan = "{}"
    
    # 尝试解析策略计划中的信息
    try:
        plan_data = json.loads(plan)
        # Check if we have options
        if "options" in plan_data:
             steps.append({"step": "options", "content": f"生成了 {len(plan_data['options'])} 个选题方案"})
        else:
            steps.append({"step": "identified", "content": f"识别痛点: {plan_data.get('pain_point', '分析中')}"})
            steps.append({"step": "angle", "content": f"切入角度: {plan_data.get('hook_angle', '构思中')}"})
    except:
        steps.append({"step": "planning", "content": "生成内容策略计划..."})
    
    steps.append({"step": "completed", "content": "策略规划完成"})
    
    return {
        "strategy_plan": plan,
        "strategy_json": plan,  # 保存原始 JSON 供 writer 使用
        "logs": [f"[{datetime.now().isoformat()}] Strategist generated plan."],
        "thinking_steps": [{"agent": "strategist", "steps": steps, "status": "completed"}]
    }

# 2. 写手节点
async def node_writer(state: AgentState):
    from .agents.writer import writer_agent
    import asyncio
    
    print("--- [Step 2] Writer is Drafting ---")
    
    # 记录思考步骤
    steps = []
    current_draft = state.get("draft_v1", "")
    is_rewrite = bool(current_draft and state.get("critique_feedback", ""))
    
    if is_rewrite:
        steps.append({"step": "rewriting", "content": f"根据主编反馈进行第 {state.get('revision_count', 0) + 1} 次修订..."})
    else:
        steps.append({"step": "loading", "content": f"加载风格模板: {state['mode']}"})
        steps.append({"step": "drafting", "content": "开始撰写初稿..."})
    
    # 获取配置
    global_config = state.get('api_config', {})
    specific_config = state.get('agent_config', {}).get('writer', {})
    effective_config = specific_config if specific_config.get("provider") else global_config
    
    print(f"--- [Step 2] Writer Config: {effective_config.get('provider')} ---")
    
    # 传递特定的 agent state
    agent_state = state.copy()
    agent_state['api_config'] = effective_config
    
    # P12.2 Fix: Run sync writer_agent in thread pool to avoid blocking asyncio loop
    # This prevents SSE stream from hanging/timing out during long generation
    try:
        result = await asyncio.to_thread(writer_agent, agent_state)
    except Exception as e:
        result = {"error": str(e)}
        print(f"--- [Step 2] Writer Error: {e} ---")
    
    # 从结果中提取 draft
    draft = result.get("draft_content", "") if isinstance(result, dict) else str(result)
    
    word_count = len(draft)
    steps.append({"step": "generated", "content": f"生成内容: {word_count} 字"})
    steps.append({"step": "completed", "content": "初稿完成，提交主编审核"})
    
    return {
        "draft_v1": draft, 
        "revision_count": state.get("revision_count", 0) + 1,
        "logs": [f"[{datetime.now().isoformat()}] Writer drafted/rewrote version {state.get('revision_count', 0) + 1}."],
        "thinking_steps": [{"agent": "writer", "steps": steps, "status": "completed"}]
    }

# 3. 毒舌主编节点
def node_critic(state: AgentState):
    from .agents.critic import critic_agent
    print("--- [Step 3] Critic is Reviewing ---")
    
    # 记录思考步骤
    steps = []
    # 获取配置
    global_config = state.get('api_config', {})
    specific_config = state.get('agent_config', {}).get('critic', {})
    
    # P12.1 优化: 如果特定配置没有 api_key，回退到全局配置
    if specific_config.get("provider") and specific_config.get("api_key"):
        effective_config = specific_config
    else:
        effective_config = global_config
    
    print(f"--- [Step 3] Critic Config: {effective_config.get('provider')} ---")
    
    steps.append({"step": "reviewing", "content": "审核内容质量..."})
    
    score, feedback = critic_agent(state["draft_v1"], state["mode"], effective_config)
    
    steps.append({"step": "scored", "content": f"评分: {score}/100"})
    
    if score < 90:
        steps.append({"step": "feedback", "content": f"反馈: {feedback[:50]}..." if len(feedback) > 50 else f"反馈: {feedback}"})
        steps.append({"step": "decision", "content": "需要修改，打回重写"})
    else:
        steps.append({"step": "approved", "content": "质量达标，通过审核"})
    
    return {
        "critique_score": score, 
        "critique_feedback": feedback,
        "logs": [f"[{datetime.now().isoformat()}] Critic score: {score}."],
        "thinking_steps": [{"agent": "critic", "steps": steps, "status": "completed"}]
    }

# 4. 润色节点
def node_polisher(state: AgentState):
    from .agents.polisher import polisher_agent
    print("--- [Step 4] Polisher is Refining ---")
    
    # 记录思考步骤
    steps = []
    # 获取配置
    global_config = state.get('api_config', {})
    specific_config = state.get('agent_config', {}).get('polisher', {})
    effective_config = specific_config if specific_config.get("provider") else global_config
    
    print(f"--- [Step 4] Polisher Config: {effective_config.get('provider')} ---")
    
    steps.append({"step": "polishing", "content": "进行最终润色..."})
    steps.append({"step": "injecting", "content": "注入 Web3 行业术语..."})
    
    final = polisher_agent(state["draft_v1"], state["critique_feedback"], effective_config)
    
    steps.append({"step": "formatting", "content": "格式化 Markdown..."})
    steps.append({"step": "completed", "content": f"最终内容: {len(final)} 字"})
    
    return {
        "final_content": final,
        "logs": [f"[{datetime.now().isoformat()}] Polisher finished."],
        "thinking_steps": [{"agent": "polisher", "steps": steps, "status": "completed"}]
    }

# 路由逻辑：Critic 决定是重写还是通过
def router_logic(state: AgentState):
    if state.get("critique_score", 0) < 90 and state.get("revision_count", 0) < 3:
        return "writer"  # 打回重写
    return "polisher"    # 通过

# 构建图
workflow = StateGraph(AgentState)

workflow.add_node("strategist", node_strategist)
workflow.add_node("writer", node_writer)
workflow.add_node("critic", node_critic)
workflow.add_node("polisher", node_polisher)

workflow.set_entry_point("strategist")
workflow.add_edge("strategist", "writer")
workflow.add_edge("writer", "critic")
workflow.add_conditional_edges(
    "critic",
    router_logic,
    {
        "writer": "writer",
        "polisher": "polisher"
    }
)
workflow.add_edge("polisher", END)

app_graph = workflow.compile()
