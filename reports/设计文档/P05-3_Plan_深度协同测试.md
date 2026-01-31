# Phase 8: 深度协同测试与体验增强计划 (Deep Integration & UX Enhancement)

> **问题**: 后端 "Deep Analysis" 产生的核心上下文 (数据锚点、风格指导) 及 "Critical Thinking" (Critic 反馈) 目前在前端不可见，导致用户感知不到 AI 的"深度"。
> **目标**: 打通后端智能数据到前端 UI 的"最后一公里"，实现真正的"透明化思考"。

---

## 1. 缺口分析 (Gap Analysis)

通过对比 `analysis_result.json` (Backend) 与 `StrategySelector.tsx` (Frontend)，发现以下关键数据丢失：

| 数据字段 (Backend) | 含义 | 前端现状 | 影响 |
| :--- | :--- | :--- | :--- |
| `info_anchors.must_mention` | **信息锚点** (E.g. "JustLend", "10.96%") | ❌ **完全忽略** | 用户不知道 AI 提取了哪些关键事实，缺乏信任感。 |
| `info_anchors.can_extend` | **延伸思考** (E.g. "通缩模型对比") | ❌ **完全忽略** | 用户错失了引导 AI 进行更有深度探讨的机会。 |
| `style_notes` | **风格指导** (E.g. "KV语言，短句轰炸") | ❌ **完全忽略** | 用户无法确认 AI 是否真的理解了"咪蒙风格"。 |
| `logs` (Agent Update) | **执行日志** (E.g. "Critic: Refused due to boring tone") | ❌ **仅显示状态** | 用户不知道 Critic 为什么要修改文章，这也是"Agentic"的核心魅力所在。 |

---

## 2. 实施方案 (Implementation Plan)

### 2.1 Store 增强 (`useAgentStore.ts`)
- **State Update**:
  ```typescript
  interface AgentState {
      // ...
      analysisResult: {       // [NEW] 存储完整的分析结果
          info_anchors: InfoAnchors;
          style_notes: string;
      } | null;
      agentLogs: string[];    // [NEW] 存储关键节点的执行日志
  }
  ```
- **Action Update**:
  - `handleEvent` ('analysis_result'): 同时保存 `info_anchors` 和 `options`。
  - `handleEvent` ('agent_update'): 将 `logs` 追加到 `agentLogs` 或通过 Toast/Timeline 展示。

### 2.2 UI 组件增强
1.  **[NEW] `ContextPanel.tsx`**:
    -   位于 `StrategySelector` 上方。
    -   展示 "🎯 Must Mention" (Tags 样式)。
    -   展示 "🎭 Style Guide" (引用样式)。
    -   *目的*: 让用户一眼看到 AI 的"调研笔记"。
2.  **[MOD] `AgentTimeline.tsx`**:
    -   支持展开查看每个步骤的 "Log Details"。
    -   当 Critic 打回重写时，显示高亮的 Warning Log。

---

## 3. 验证计划 (Verification Plan)

### 3.1 自动化验证
- **Mock Data**: 使用 `analysis_result.json` 作为 Mock 数据源。
- **Test Case**: 启动前端，注入 Mock 数据，验证 `ContextPanel` 是否正确渲染 "JustLend" 和 "10.96%"。

### 3.2 人工验收
- 执行 `Phase 7` 同款 "JustLend + Mimeng" 测试。
- **验收标准**:
    1.  用户在选择策略前，能看到 AI 提取的 "10.96%" 无需用户输入。
    2.  Timeline 中能看到 Critic 的具体“吐槽”（如有）。
