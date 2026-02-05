from typing import TypedDict, Annotated, List, Union, Dict, Any
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime
import json

# P14: 导入模式配置
from .core.mode_configs import get_mode_config, MODE_CONFIGS

# P16.1: 移除旧的 LENGTH_MAP, MODE_LENGTH_MAPPING, enforce_mode_length, calculate_length
# 字数约束现在完全由 mode_configs.py 控制，在 Writer/Critic/Polisher 中使用

# 定义状态字典
class AgentState(TypedDict):
    raw_input: str
    mode: str  # "hot_take", "mid_article", "long_article", "tutorial", "rewrite"  # P16: 模式改名
    style: str  # P10: "auto", "mimeng", "banfo", "xinshixiang", "insider"
    length: Union[str, None]  # @deprecated P11: "tweet", "thread", "post"
    custom_length: int  # P16: 自定义字数 (0=使用模式默认)
    retention_level: int  # P10: 保留度等级 1-5
    narrative_type: str  # 新增：叙事类型
    references: List[str]  # P3: 选题参考列表
    selected_option: Dict[str, Any] # P4: 用户选择的选题方案
    api_config: Dict[str, Any]  # 默认/全局 API 配置
    agent_config: Dict[str, Dict[str, Any]]  # 新增：每个 Agent 的特定配置
    custom_prompts: Dict[str, str]  # P15: 自定义提示词
    strategy_plan: str
    strategy_json: str  # 新增：策略 JSON（用于传递给 writer）
    web3_knowledge: str # [P12] 新增：Web3 知识上下文 (from Strategist -> Writer)
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
            "web3_knowledge": "", # 选中方案模式下暂不回溯检索 (未来可优化)
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
        # [P12 Refactor] strategist_agent now returns a dict: {"plan": str, "web3_knowledge": str}
        result = strategist_agent(agent_state)
        if isinstance(result, dict) and "plan" in result:
             plan = result["plan"]
             web3_knowledge = result.get("web3_knowledge", "")
        else:
             # Backward compatibility fallback
             plan = str(result)
             web3_knowledge = ""
    except Exception as e:
         steps.append({"step": "error", "content": f"Strategist Error: {str(e)}"})
         plan = "{}"
         web3_knowledge = ""
    
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
    
    if web3_knowledge:
        steps.append({"step": "knowledge", "content": f"已检索 Web3 知识库"})

    steps.append({"step": "completed", "content": "策略规划完成"})
    
    return {
        "strategy_plan": plan,
        "strategy_json": plan,  # 保存原始 JSON 供 writer 使用
        "web3_knowledge": web3_knowledge, # 传递给 Writer
        "logs": [f"[{datetime.now().isoformat()}] Strategist generated plan."],
        "thinking_steps": [{"agent": "strategist", "steps": steps, "status": "completed"}]
    }

# 2. 写手节点 (P18: 使用模块化路由)
async def node_writer(state: AgentState):
    from .agents.writer import get_writer
    from .agents.writer import writer_agent  # Fallback for rewrite loops
    import asyncio
    
    print("--- [Step 2] Writer is Drafting ---")
    
    # 记录思考步骤
    steps = []
    current_draft = state.get("draft_v1", "")
    is_rewrite = bool(current_draft and state.get("critique_feedback", ""))
    mode = state.get("mode", "mid_article")
    
    if is_rewrite:
        steps.append({"step": "rewriting", "content": f"根据主编反馈进行第 {state.get('revision_count', 0) + 1} 次修订..."})
        # 修订时仍使用旧 writer_agent (保持修订逻辑不变)
        writer_fn = writer_agent
    else:
        steps.append({"step": "loading", "content": f"加载模块: writer/{mode}"})
        steps.append({"step": "drafting", "content": "开始撰写初稿..."})
        # P18: 使用模块化路由获取对应 Writer
        writer_fn = get_writer(mode)
    
    # 获取配置
    global_config = state.get('api_config', {})
    specific_config = state.get('agent_config', {}).get('writer', {})
    effective_config = specific_config if specific_config.get("provider") else global_config
    
    print(f"--- [Step 2] Writer Config: {effective_config.get('provider')}, Mode: {mode} ---")
    
    # 传递特定的 agent state
    agent_state = state.copy()
    agent_state['api_config'] = effective_config
    
    # P12.2 Fix: Run sync writer in thread pool to avoid blocking asyncio loop
    try:
        result = await asyncio.to_thread(writer_fn, agent_state)
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

# 3. 毒舌主编节点 (P18: 使用模块化路由)
def node_critic(state: AgentState):
    from .agents.critic import get_critic
    print("--- [Step 3] Critic is Reviewing ---")
    
    mode = state.get("mode", "mid_article")
    
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
    
    print(f"--- [Step 3] Critic Config: {effective_config.get('provider')}, Mode: {mode} ---")
    
    steps.append({"step": "loading", "content": f"加载模块: critic/{mode}"})
    steps.append({"step": "reviewing", "content": "审核内容质量..."})
    
    # P10: 传递 length 和 style 参数给 Critic
    length = state.get("length", "medium")
    style = state.get("style", "auto")
    
    # P18: 使用模块化路由获取对应 Critic
    critic_fn = get_critic(mode)
    critic_result = critic_fn(
        draft=state["draft_v1"], 
        mode=mode, 
        api_config=effective_config,
        length=length,
        style=style,
        custom_prompts=state.get("custom_prompts", {})
    )
    
    # P12: 从 dict 中提取结果
    if isinstance(critic_result, dict):
        score = critic_result.get("score", 0)
        verdict = critic_result.get("verdict", "REFINE")
        suggestions = critic_result.get("suggestions", [])
        # 将 suggestions 转为字符串传给 Polisher
        feedback = verdict + ": " + "; ".join(suggestions) if suggestions else verdict
    else:
        # 兼容旧代码 (如果回滚)
        score, feedback = critic_result
        verdict = "PASS" if score >= 85 else "REFINE" if score >= 70 else "REWRITE"
    
    steps.append({"step": "scored", "content": f"评分: {score}/100 ({verdict})"})
    
    # P12: 阈值从 90 改为 85
    PASS_THRESHOLD = 85
    if score < PASS_THRESHOLD:
        feedback_preview = feedback[:50] + "..." if len(feedback) > 50 else feedback
        steps.append({"step": "feedback", "content": f"反馈: {feedback_preview}"})
        steps.append({"step": "decision", "content": f"需要修改 ({verdict})"})
    else:
        steps.append({"step": "approved", "content": "质量达标，通过审核 (PASS)"})
    
    return {
        "critique_score": score, 
        "critique_feedback": feedback,
        "critique_verdict": verdict,  # P12: 新增 verdict 字段
        "critique_result": critic_result if isinstance(critic_result, dict) else {},  # P12: 保存完整结果
        "logs": [f"[{datetime.now().isoformat()}] Critic score: {score} ({verdict})."],
        "thinking_steps": [{"agent": "critic", "steps": steps, "status": "completed"}]
    }

# 4. 润色节点 (P18: 使用模块化路由)
def node_polisher(state: AgentState):
    from .agents.polisher import get_polisher
    print("--- [Step 4] Polisher is Refining ---")
    
    mode = state.get("mode", "mid_article")
    
    # 记录思考步骤
    steps = []
    # 获取配置
    global_config = state.get('api_config', {})
    specific_config = state.get('agent_config', {}).get('polisher', {})
    effective_config = specific_config if specific_config.get("provider") else global_config
    
    print(f"--- [Step 4] Polisher Config: {effective_config.get('provider')}, Mode: {mode} ---")
    
    steps.append({"step": "loading", "content": f"加载模块: polisher/{mode}"})
    steps.append({"step": "polishing", "content": "进行最终润色..."})
    steps.append({"step": "injecting", "content": "注入 Web3 行业术语..."})
    
    # P16.1: 获取字数约束传递给 Polisher
    mode_config = get_mode_config(mode)
    length_constraints = mode_config.get("length", {"min": 150, "max": 800, "target": 500})
    
    # P18: 使用模块化路由获取对应 Polisher
    polisher_fn = get_polisher(mode)
    final = polisher_fn(
        draft=state["draft_v1"], 
        critique_feedback=state["critique_feedback"], 
        api_config=effective_config,
        custom_prompts=state.get("custom_prompts", {}),
        mode=mode,
        length_constraints=length_constraints
    )
    
    steps.append({"step": "formatting", "content": "格式化 Markdown..."})
    steps.append({"step": "completed", "content": f"最终内容: {len(final)} 字"})
    
    return {
        "final_content": final,
        "logs": [f"[{datetime.now().isoformat()}] Polisher finished."],
        "thinking_steps": [{"agent": "polisher", "steps": steps, "status": "completed"}]
    }

# 路由逻辑：Critic 决定是重写还是通过 (P14: 模式感知)
def router_logic(state: AgentState):
    mode = state.get("mode", "mid_article")  # P16: 默认中篇
    config = get_mode_config(mode)
    
    # P14: 如果模式跳过评审，直接进润色
    if config.get("skip_critic", False):
        return "polisher"
    
    # P14: 获取模式专属阈值
    scoring = config.get("scoring", {})
    pass_threshold = scoring.get("pass_threshold", 85)
    max_revisions = scoring.get("max_revisions", 3)
    
    # P14-Fix7: 使用模式专属阈值
    if state.get("critique_score", 0) < pass_threshold and state.get("revision_count", 0) < max_revisions:
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
