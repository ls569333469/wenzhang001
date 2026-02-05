# P20 - 事件脉络感知 (Context Card) 最终方案

## 1. 问题背景：信息孤岛

用户反馈显示，当 `Writer` 智能体在"真空"中运作时，写作质量会下降——它将孤立的数据点（信息锚点）视为独立事实，无法理解事件的"前因后果"。

## 2. 解决方案：脉络还原

将 `Strategist` 智能体的职责从简单提取转变为**叙事重建**。

### 2.1 事件脉络卡片 (context_card) 结构

Strategist 必须在 JSON 计划中输出结构化的 `context_card` 字段：

| 字段 | 必填? | 说明 |
| :--- | :--- | :--- |
| **has_event** | ✅ | 是否有具体爆发性事件（科普/教程类为 `false`） |
| **summary** | ✅ | 一句话脉络摘要（时间+核心事实+当前背景）。合并了原有的起因和现状 |
| **time_context** | ✅ | 时效性标签：`Today` / `Recent` / `Historical` / `Null` |
| **forward_look** | ❌ | 可选，可能的后续发展或影响 |

### 2.2 全局输出扩展（综合审计）

根据用户反馈和 Grok 方案对比，Strategist 的 JSON 输出包括：
- **`context_card`**：结构化的情景感知
- **`recommended_option_id`**：主要策略方向标识（`option_1`、`option_2` 等），用于 UI 高亮显示
- **`risk_notes`**：合规或事实风险列表（如"避免价格预测"、"核实日期来源"）

### 2.3 时效性判断逻辑

为克服 LLM 搜索延迟（如 Gemini 约 24 小时延迟）：

1. **当前锚点**：后端将 `current_time` 字符串注入提示词
2. **第一阶段（当前）**：**用户辅助**。用户在 UI 中选择时效性，`manual_time_hint` 确保 Strategist 获得基准时间锚点
3. **第二阶段（展望）**：待 Gemini 提示词迭代稳定后，评估自动脉络检测
4. **验证逻辑**：Strategist 必须将 `manual_time_hint` 与素材中提取的事实交叉验证，填充 `summary`

### 2.4 机制：上下文注入

不限制写作者的选项（降级），而是提供"简报"，写作者在起草每个段落前必须参考。

#### 策略指令示例：
> "注意：当前事件已过去 72 小时。素材描述的'宕机'已是旧闻。你的写作环境是'震荡后的反思期'。不要使用'突发'、'刚刚'等词汇，应侧重于'事故暴露出的长期结构性矛盾'。"

### 2.5 "1+2 组合" 实现

为确保结构稳定性和叙事深度，系统采用两阶段注入模式：

1. **阶段 2（Strategist）**：生成结构化的 `context_card` 作为标准 JSON 对象
2. **阶段 1（Writer）**：系统自动将 `context_card` 作为专用模块重新注入到 Writer 提示词的开头

**实现逻辑**：
- **Strategist 节点**：评估用户输入 + `current_time` → 产生包含 `context_card` 的 JSON
- **Writer 节点**：模板前置 `{% if context_card %} ## 当前事件脉络卡片 {{ context_card | tojson }} {% endif %}`

## 3. 实现里程碑

- [x] **方案定稿**：中文翻译已获利益相关者批准
- [ ] **Strategist 更新**：在 `strategist.jinja2` schema 中添加 `context_card`
- [ ] **Writer 更新**：全局模板更新以注入 `context_card`
- [ ] **Critic 集成**：在 Polished 版本中惩罚"时间漂移"或"上下文不一致"

---

> **文档版本**：V1（最终方案）  
> **创建日期**：2026-02-05  
> **来源**：基于 `situational_awareness_v1.md` 蓝图翻译
