# Phase 8: 真实规模化测试验证计划 (Large Scale Verification Plan)

> **目标**: 在真实高并发、多场景下验证系统的稳定性与内容质量。
> **现状**: 前端功能完备，后端仅支持 Lark 数据源，缺乏实时联网搜索能力。

---

## 1. 测试范围 (Scope)

我们将模拟 **"Web3 媒体主编"** 的真实工作流，进行批量化内容生产测试。

| 维度 | 规模/指标 | 说明 |
| :--- | :--- | :--- |
| **并发量** | 10 Concurrent Requests | 模拟小型编辑部同时工作 |
| **总批次** | 50 Articles | 覆盖不同赛道 (DeFi, Macro, Meme) |
| **风格覆盖** | 3 Styles | Mimeng (爆款), Research (研报), News (快讯) |
| **输入源** | Lark Records + Custom | 混合使用 Lark 现有素材和人工合成指令 |

---

## 2. 缺口分析 (Gap Analysis)

在执行"真实"测试前，必须解决以下缺失能力：

### 🔴 关键缺失 (Critical)
1.  **Web Search Integration**: 目前后端无联网能力。真实创作需要实时校验数据 (e.g. 币价、最新推文)。
    -   *Plan*: 集成 `Serper` 或 `Tavily` API 到 Strategist 节点。
2.  **Concurrency Support**: `main.py` 是 Async 的，但 Graph 节点内部是否有阻塞代码需复查。
3.  **Cost Monitoring**: 批量测试会消耗大量 Token (预计 50篇 x 10k tokens = 500k tokens)。需集成 Cost Tracker。

---

## 3. 测试方案 (Test Strategy)

### 3.1 准备阶段 (Preparation)
- **脚本开发**: 开发 `stress_test.py`，支持多线程发送 `/analyze` 和 `/generate` 请求。
- **数据准备**: 编写 `test_prompts.csv`，包含 50 条真实的 Web3 选题指令。
- **API Key**: 确保 Volcengine/DeepSeek 余额充足。

### 3.2 执行阶段 (Execution)
1.  **Baseline Test**: 单线程跑 5 篇，确立基准耗时 (e.g. 45s/篇)。
2.  **Load Test**: 10 线程并发，观察后端错误率 (500/429) 和响应时间 (Latency P99)。
3.  **Quality Check**: 人工抽检 20% 生成内容，评分维度：
    -   数据准确性 (Hallucination Rate)
    -   风格一致性 (Style Adherence)
    -   重复率 (Repetition Rate)

---

## 4. 资源需求 (Resource Requirements)
- **Budget**: 预计消耗 $5 - $10 (DeepSeek V3 API).
- **Time**: 开发脚本 (2h) + 测试执行 (1h) + 结果分析 (1h)。
- **Tools**: `locust` (可选负载工具) 或自定义 Python 脚本。

---

## 5. 待确认事项 (Action Items)
- [ ] 是否需要立即集成 **Web Search**？(这将改变后端架构)
- [ ] 是否有足够的 **Lark 记录** 用于 RAG 测试？(目前仅连接成功，未验证数量)
- [ ] 是否授权进行 **高并发 API 调用**？(需确认 Key 的限流策略)
