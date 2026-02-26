# P31: 投研模式 LangGraph 管线设计

> 创建时间: 2026-02-27 01:15 | 状态: 待实施
> 上一版设计方案见本文件上半部分（v1 架构），本节为 v2 LangGraph 集成方案

## 目标

投研模式（`project_research`）像锐评/短篇/中篇一样，完整走 LangGraph 管线，在 Studio 前端运行和迭代。

## 投研管线（`project_research` 专用）

```
              ┌── 无输入 → Scout(选题发现,Surf API) ──┐
entry_router ─┤                                      ├→ Strategist → Writer → Critic → Polisher
              └── 有输入(项目名) → 直接跳过 ──────────┘
```

**关键区别**：投研模式在 Strategist 之前多一个 **Scout 节点**。其余节点复用现有 LangGraph 基础设施。

---

## 节点设计

### Node 0: Scout（选题发现） — 新增

> 仅 `project_research` 模式有此节点，其他模式跳过

| 项 | 值 |
|----|-----|
| 触发条件 | `mode == "project_research"` 且 `raw_input` 为空 |
| API | Surf API (`surf-1.5`) |
| 能力 | `search` |
| 输入 | `raw_input`（可为空，表示自动从 leak.me 发现） |
| 输出 | `scout_projects: list[dict]` — 发现的项目列表 |
| Prompt | `data/prompts/research/scout.jinja2`（已有） |
| 前端 SSE | `{"step": "scout", "content": "发现 5 个热门项目..."}` |

**逻辑**：
- 如果 `raw_input` 有具体项目名 → 跳过 Scout，直接进 Strategist
- 如果 `raw_input` 为空或为"自动选题" → 调 Surf API 搜 leak.me → 输出项目列表

### Node 1: Strategist（深度分析） — 复用+扩展

| 项 | 值 |
|----|-----|
| API | Surf API (`surf-1.5`, reasoning=high) |
| Prompt | `data/prompts/strategist/project_research.jinja2`（需新建） |
| 输入 | `raw_input`（项目名）或 Scout 输出 |
| 输出 | `strategy_json` — 结构化分析数据 |

在 `strategist.py` 的 `build_strategist_prompt` 中加 `project_research` 分支：
```python
elif mode == "project_research":
    context["raw_input"] = combined_input
    system_prompt = render_prompt("strategist/project_research", context)
    user_prompt = f"[Session: {random_seed}]\n请对该项目进行全维度投研分析。"
```

### Node 2-4: Writer / Critic / Polisher — 全部已有 ✅

| 节点 | 文件 | 模板 |
|------|------|------|
| Writer | `agents/writer/project_research.py` ✅ | `writer/project_research.jinja2` ✅ |
| Critic | `standard_critic` ✅ | `critic/project_research.jinja2` ✅ |
| Polisher | `standard_polisher` ✅ | `polisher/project_research.jinja2` ✅ |

---

## AgentState 扩展

```python
class AgentState(TypedDict):
    # ... 现有字段不变 ...
    # P31: 投研模式新增
    scout_projects: List[Dict[str, Any]]  # Scout 发现的项目列表
```

## graph.py 改造

```python
# 新增 Scout 节点
def node_scout(state: AgentState):
    from .agents.research.scout import scout_agent
    return scout_agent(state)

# 路由：是否需要 Scout
def entry_router(state: AgentState):
    mode = state.get("mode", "mid_article")
    raw_input = state.get("raw_input", "")
    if mode == "project_research" and not raw_input.strip():
        return "scout"
    return "strategist"

# 构建图
workflow.add_node("scout", node_scout)
workflow.set_conditional_entry_point(
    entry_router,
    {"scout": "scout", "strategist": "strategist"}
)
workflow.add_edge("scout", "strategist")
```

---

## 前端 Settings 映射

| Pipeline 节点 | Settings 配置位 | 状态 |
|--------------|----------------|------|
| Scout | 新增或复用 Strategist 位 | 需确认 |
| Strategist | `project_research.strategist` | ✅ 已有 |
| Writer | `project_research.writer` | ✅ 已有 |
| Critic | `project_research.critic` | ✅ 已有 |
| Polisher | `project_research.polisher` | ✅ 已有 |

## 需要新增/修改的文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `agents/research/scout.py` | **新增** | Scout 智能体（调 Surf API） |
| `agents/research/__init__.py` | **新增** | 模块入口 |
| `graph.py` | **修改** | 加 scout 节点 + entry_router |
| `agents/strategist.py` | **修改** | 加 `project_research` 分支 |
| `data/prompts/strategist/project_research.jinja2` | **新增** | 策略官投研专用模板 |

## 不需要改的（P27 已预留）

- Writer/Critic/Polisher → 节点+模板全部已有
- 前端 PromptEditor/AgentModelConfig → 已有「投研」Tab
- mode_configs.py → `project_research` 配置已有
