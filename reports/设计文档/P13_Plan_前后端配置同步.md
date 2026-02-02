# P13 Plan - 前后端配置同步

**创建日期**: 2026-01-31  
**状态**: 📝 规划中  
**执行人**: Antigravity  
**总工时**: ~7.5 小时

---

## 📖 目录

1. [问题总览](#-问题总览)
2. [10个解决方案](#-10个解决方案)
3. [审核检查表](#-审核检查表)
4. [附录：排查详情](#附录排查详情)

---

## 📊 问题总览

### 发现的问题统计

| 类别 | 问题数 | 严重 🔴 |
|------|:------:|:-------:|
| A. 请求参数缺失 | 5 | 3 |
| B. 枚举值域不一致 | 4 | 1 |
| C. SSE 事件缺失 | 2 | 1 |
| D. 类型定义缺失 | 6 | 2 |
| E. 配置同步问题 | 5 | 2 |
| F. P12 透传问题 | 5 | 1 |
| **合计** | **27** | **10** |

### Top 5 严重问题

| # | 问题 | 影响 |
|---|------|------|
| 1 | `api_config` / `agent_config` 未传 | 无法控制 AI 模型选择 |
| 2 | 8/10 style 无后端样本 | 风格选择形同虚设 |
| 3 | Settings 页面单 Provider | 无法配置多模型 |
| 4 | P12 评分无 SSE 事件 | 五维度数据无法展示 |
| 5 | 前端缺 APIConfigSchema | 类型定义不完整 |

---

## 🛠️ 10个解决方案

### 方案 1: `/analyze` 添加 retention_level ⏱️5min

**问题**: /analyze 请求缺少 retention_level  
**文件**: `useAgentStore.ts` L157-165

```typescript
const requestBody = {
    input: finalInput,
    mode: config.mode || 'deep_analysis',
    style: config.style || 'mimeng',
    length: config.length || 'thread',
    retention_level: config.retention_level || 3,  // ✅ 新增
    narrative_type: 'project_review',
    references: [],
};
```

---

### 方案 2: 新增 APIConfigSchema ⏱️30min

**问题**: 前端缺少 API 配置类型定义  
**文件**: `schema.ts`

```typescript
export const AIProviderSchema = z.enum(['google', 'volcengine', 'deepseek', 'openai']);

export const APIConfigSchema = z.object({
    provider: AIProviderSchema.default('volcengine'),
    model_id: z.string().optional(),
    api_key: z.string().optional(),
});

export const AgentConfigSchema = z.object({
    strategist: APIConfigSchema.optional(),
    writer: APIConfigSchema.optional(),
    critic: APIConfigSchema.optional(),
    polisher: APIConfigSchema.optional(),
});
```

---

### 方案 3: useAgentStore 传递配置 ⏱️30min

**问题**: requestBody 缺少 api_config 和 agent_config  
**文件**: `useAgentStore.ts`

```typescript
const getAgentConfig = () => {
    const stored = localStorage.getItem('qs_agent_config');
    if (stored) {
        try { return JSON.parse(stored); } 
        catch { return undefined; }
    }
    return undefined;
};

const requestBody = {
    // ...existing fields...
    api_config: config.api_config,      // ✅ 新增
    agent_config: getAgentConfig(),     // ✅ 新增
};
```

---

### 方案 4: Settings 页面重构 ⏱️3h

**问题**: 当前仅支持单 Provider  
**文件**: `settings/page.tsx` (重构)

```
┌─────────────────────────────────────────────────────┐
│ 模型提供商配置                                        │
├─────────────────────────────────────────────────────┤
│ [Gemini ✓] [ARK] [DeepSeek] [OpenAI]                │
│                                                     │
│ API Key: [AIzaSy...                            ]   │
│ 默认模型: [gemini-2.5-flash ▼]                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Agent 模型分配                                       │
├─────────────────────────────────────────────────────┤
│ 策略师:  [Gemini ▼]   写手:    [ARK ▼]             │
│ 评论家:  [ARK ▼]      润色师:  [ARK ▼]             │
└─────────────────────────────────────────────────────┘
```

---

### 方案 5: 后端 /config/agents API ⏱️1h

**问题**: 缺少获取/保存 Agent 配置的 API  
**文件**: `main.py`

```python
@app.get("/config/agents")
async def get_agent_config():
    config = load_user_config()
    return {
        "strategist": config.get("strategist", {"provider": "google"}),
        "writer": config.get("writer", {"provider": "volcengine"}),
        "critic": config.get("critic", {"provider": "volcengine"}),
        "polisher": config.get("polisher", {"provider": "volcengine"})
    }

@app.post("/config/agents")
async def save_agent_config(config: Dict[str, APIConfig]):
    user_config = load_user_config()
    for name, cfg in config.items():
        user_config[name] = cfg.dict()
    save_user_config(user_config)
    return {"status": "ok"}
```

---

### 方案 6: critique_update SSE 事件 ⏱️1h

**问题**: P12 评分数据无专用 SSE 事件  
**文件**: `main.py`

```python
# 在 /generate 的 astream 循环中
if node_name == "critic" and "critique_score" in node_state:
    critique_data = {
        "type": "critique_update",
        "score": node_state.get("critique_score", 0),
        "verdict": node_state.get("verdict"),
        "dimensions": node_state.get("dimensions", {}),
        "penalties": node_state.get("penalties", []),
        "suggestions": node_state.get("suggestions", [])
    }
    yield f"data: {json.dumps(critique_data)}\n\n"
```

---

### 方案 7: 前端处理 critique_update ⏱️30min

**问题**: 前端无法处理 critique_update 事件  
**文件**: `useAgentStore.ts`

```typescript
case 'critique_update': {
    set({
        critiqueResult: {
            score: event.score,
            verdict: event.verdict,
            dimensions: event.dimensions,
            penalties: event.penalties,
            suggestions: event.suggestions
        }
    });
    break;
}
```

---

### 方案 8: CritiquePanel UI 组件 ⏱️2h

**问题**: 无评分展示 UI  
**新增文件**: `components/CritiquePanel.tsx`

```tsx
export function CritiquePanel({ result }) {
    if (!result) return null;
    return (
        <Card>
            <Badge>{result.score}分 - {result.verdict}</Badge>
            {/* 五维度进度条 */}
            {Object.entries(result.dimensions).map(([dim, score]) => (
                <Progress key={dim} label={dim} value={score} />
            ))}
            {/* 扣分项 & 建议 */}
        </Card>
    );
}
```

---

### 方案 9: style fallback 提示 ⏱️15min

**问题**: 选择无样本 style 时静默 fallback  
**文件**: `writer.py`

```python
if not samples and style != "mimeng":
    samples = sample_service.get_samples(style="mimeng", count=3)
    # ✅ 新增提示
    thinking_steps.append({
        "agent": "writer",
        "steps": [{"step": "fallback", 
                   "content": f"⚠️ 未找到「{style}」样本，使用咪蒙体"}]
    })
```

---

### 方案 10: 添加 tutorial mode ⏱️10min

**问题**: 前端缺少 tutorial 模式  
**文件**: `schema.ts`

```typescript
export const CreationModeSchema = z.enum([
    'deep_analysis',
    'quick_summary',
    'rewrite',
    'translate',
    'tutorial',  // ✅ 新增
]);
```

---

## ✅ 审核检查表

| # | 方案 | 工时 | 执行? | 备注 |
|---|------|:----:|:----:|------|
| 1 | /analyze 添加 retention_level | 5min | [x] | ✅ Claude 已完成 |
| 2 | 新增 APIConfigSchema | 30min | [x] | ✅ Claude 已完成 |
| 3 | useAgentStore 传递配置 | 30min | [x] | ✅ Claude 已完成 |
| 4 | Settings 页面重构 | 3h | [ ] | 🟡 工作量大，待 P14 |
| 5 | 后端 /config/agents API | 1h | [x] | ✅ Claude 已完成 |
| 6 | critique_update SSE 事件 | 1h | [x] | ✅ Claude 已完成 |
| 7 | 前端处理 critique_update | 30min | [x] | ✅ Claude 已完成 |
| 8 | CritiquePanel 组件 | 2h | [ ] | 🟡 待 P14 |
| 9 | style fallback 提示 | 15min | [x] | ✅ Claude 已完成 |
| 10 | 添加 tutorial mode | 10min | [x] | ✅ Claude 已完成 |
| **+** | **输入过滤 sanitize_input** | 30min | [x] | ✅ Claude 已完成 (Phase I) |

---

## 附录：排查详情

<details>
<summary>📋 Phase A: 请求参数一致性 (点击展开)</summary>

### A1. /analyze 接口字段对比

| 字段 | 后端期望 | 前端发送 | 状态 |
|------|:--------:|:--------:|:----:|
| `input` | ✅ | ✅ | ✅ |
| `mode` | ✅ | ✅ | ✅ |
| `style` | ✅ | ✅ | ✅ |
| `length` | ✅ | ✅ | ✅ |
| `retention_level` | ✅ | ❌ | 🔴 |
| `api_config` | ✅ | ❌ | 🔴 |
| `agent_config` | ✅ | ❌ | 🔴 |

### A2. /generate 接口字段对比

| 字段 | 后端期望 | 前端发送 | 状态 |
|------|:--------:|:--------:|:----:|
| `retention_level` | ✅ | ✅ | ✅ |
| `api_config` | ✅ | ❌ | 🔴 |
| `agent_config` | ✅ | ❌ | 🔴 |
| `selected_option` | ✅ | ✅ | ✅ |

</details>

<details>
<summary>📋 Phase B: 枚举值域一致性 (点击展开)</summary>

### B1. mode 值域

| 值 | 前端 | 后端 | 状态 |
|---|:---:|:---:|:---:|
| `deep_analysis` | ✅ | ✅ | ✅ |
| `quick_summary` | ✅ | ✅ | ✅ |
| `rewrite` | ✅ | ✅ | ✅ |
| `translate` | ✅ | ✅ | ✅ |
| `tutorial` | ❌ | ✅ | 🔴 |

### B2. style 值域

- 前端定义 10 种风格
- 后端仅验证 `mimeng` 和 `banfo`
- 其他 8 种会静默 fallback

### B3. length 值域

- 前端: tweet, thread, post ✅
- 后端: 同上 + 旧值 short/medium/long

</details>

<details>
<summary>📋 Phase C: SSE 事件一致性 (点击展开)</summary>

### C1. 事件类型覆盖

| 事件 | 后端 | 前端 | 状态 |
|------|:----:|:----:|:----:|
| `thinking_step` | ✅ | ✅ | ✅ |
| `agent_update` | ✅ | ✅ | ✅ |
| `analysis_result` | ✅ | ✅ | ✅ |
| `final_result` | ✅ | ✅ | ✅ |
| `error` | ✅ | ✅ | ✅ |
| `end` | ✅ | ✅ | ✅ |
| `critique_update` | ❌ | ❌ | 🔴 需新增 |

</details>

<details>
<summary>📋 Phase D-F: 类型/配置/P12 (点击展开)</summary>

### D. 类型定义

- ❌ 缺失 `APIConfigSchema`
- ❌ 缺失 `AgentConfigSchema`

### E. 配置同步

- Settings 页面只存 localStorage
- 后端实际用 user_config.json
- Model 选择不同步

### F. P12 透传

- Critic 返回完整评分 dict
- 但无专用 SSE 事件传递
- 前端无 UI 展示

</details>

---

## 🔬 扩展审计结果 (Phase G-K)

**执行时间**: 2026-01-31 22:25  
**执行人**: Antigravity

### Phase G: 输出质量 & 一致性

| 检查项 | 结果 | 状态 |
|--------|------|:----:|
| 三模型配置 | Gemini/DeepSeek/Doubao 均已配置 | ✅ |
| 风格一致性 | P12 五维度评分已实现 | ✅ |
| 多文体测试 | 仅 Web3 素材可用 | ⚠️ |

**待补充**:
- 多文体样本集 (新闻/小说/营销)
- 英文测试数据

---

### Phase H: 多 Agent 协作稳定性

| 检查项 | 结果 | 状态 |
|--------|------|:----:|
| 链路定义 | LangGraph `graph.py` 完整 | ✅ |
| 错误处理 | try-except 覆盖主要 Agent | ✅ |
| 降级机制 | 无明确 fallback | ❌ |
| trace 日志 | print 语句散落 | ⚠️ |

**当前链路**:
```
Strategist → [用户选择] → Writer → Critic → Polisher → 输出
```

---

### Phase I: Prompt 注入 & 安全检查

| 检查项 | 代码位置 | 结果 |
|--------|----------|:----:|
| 用户输入入口 | `main.py` L81 `input: str` | ❌ **无过滤** |
| Strategist 拼接 | `strategist.py` L79 | ❌ **无过滤** |
| Writer 拼接 | `writer.py` L46 `raw_input` | ❌ **无过滤** |
| Moderation API | 未集成 | ❌ |

**🔴 安全风险**: 用户输入直接进入 LLM，无 XSS/注入过滤

---

### Phase J: 多模型路由 & 一致性

| Agent | Provider | Model | 验证 |
|-------|----------|-------|:----:|
| Strategist | Google | gemini-2.5-flash | ✅ |
| Writer | Volcengine | deepseek-v3 | ✅ |
| Critic | Volcengine | doubao-1.5-pro | ✅ |
| Polisher | Volcengine | doubao-1.5-pro | ✅ |

**路由逻辑** (`writer.py` L73-75):
```python
provider = api_config.get("provider", "volcengine")
api_key = api_config.get("api_key") or None
model_id = api_config.get("model_id") or None
```

---

### Phase K: 代码健康 & 技术债扫描

**扫描工具**: radon (Python 代码复杂度分析)

#### 代码统计

| 文件 | LOC | 复杂度等级 |
|------|:----:|:----------:|
| `main.py` | 896 | 多个 A-C |
| `graph.py` | 336 | A-B |
| `writer.py` | 195 | **C (20)** 🔴 |

#### 高复杂度函数 (C 级, 需重构)

| 函数 | 文件 | 复杂度 | 问题 |
|------|------|:------:|------|
| `writer_agent` | writer.py | **C (20)** | 逻辑过于集中 |
| `get_samples` | google_sheets_source.py | **C (17)** | 多层条件嵌套 |
| `sync_from_lark` | sync_service.py | **C (15)** | 同步逻辑复杂 |
| `start_ingest` | main.py | **C (15)** | 大量条件分支 |
| `retrieve_web3_knowledge` | knowledge_retriever.py | **C (14)** | 检索逻辑复杂 |

#### 代码整体评估

```
133 blocks (classes, functions, methods) analyzed
Average complexity: A (3.66) ✅ 整体健康
```

---

## 📊 扩展审计汇总

| Phase | 内容 | 问题数 | 严重 |
|-------|------|:------:|:----:|
| G | 输出质量 | 1 | 0 |
| H | Agent 稳定性 | 2 | 1 |
| I | 安全检查 | 4 | 4 🔴 |
| J | 模型路由 | 0 | 0 |
| K | 代码健康 | 5 | 2 |
| **合计** | | **12** | **7** |

### 新增待修复任务

| 优先级 | 问题 | 建议修复 |
|:------:|------|----------|
| 🔴 1 | 无输入过滤 | 添加 sanitize_input() 函数 |
| 🔴 1 | writer_agent 复杂度 C20 | 拆分为多个辅助函数 |
| 🟡 2 | 无降级机制 | Agent 失败时 fallback |
| 🟡 2 | trace 日志散乱 | 统一 logging 模块 |
| 🟢 3 | sync_from_lark 复杂度 C15 | 提取子函数 |
| 🟢 3 | **标题/方案数量不一致** | title_candidates 3-5 个 vs options 固定 3 个，UI 展示混淆 |

---

## 📋 Gemini 审阅摘要

### 文档覆盖范围

| 类别 | 包含 |
|------|:----:|
| 前后端一致性 (Phase A-F) | ✅ |
| 系统审计 (Phase G-K) | ✅ |
| 10 个解决方案 | ✅ |
| 代码示例 | ✅ |
| 优先级排序 | ✅ |
| 工时估算 | ✅ |

### 总问题数

| 来源 | 问题数 | 严重 |
|------|:------:|:----:|
| Phase A-F (前后端) | 27 | 10 |
| Phase G-K (系统) | 12 | 7 |
| 刚发现 (UI/UX) | 1 | 0 |
| **合计** | **40** | **17** |

### 执行建议

**立即修复 (2h)**:
1. retention_level 传递 (5min)
2. critique_update SSE (1h)
3. 输入过滤 sanitize (30min)

**后续迭代**:
- Settings 多 Provider 重构 → P14
- 代码复杂度优化 → 持续
- CritiquePanel UI → P14

---

**请 Gemini 审阅**:
1. 是否有遗漏的问题类别？
2. 解决方案是否合理？
3. 优先级排序是否正确？



