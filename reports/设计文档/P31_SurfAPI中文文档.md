# P31 Surf API 中文文档

> 基于官方文档翻译整理 | 2026-02-25  
> 原始文档：`P31_SurfAPI官方文档.md`

---

## 一、平台概述

**Surf** 由 Cyber 推出，是一个 AI 驱动的加密货币情报平台，融合了链上数据、市场分析和社交情绪，为数字资产研究和执行提供实时洞察。

### 数据覆盖

| 维度 | 规模 |
|------|------|
| 区块链 | 40+ 条链 |
| 数据源 | 200+ 个 |
| 认证 KOL | 100,000+ |

### 核心能力

- 市场与技术指标
- 代币流动追踪
- 衍生品数据
- 情绪趋势分析
- 跨链监控
- 协议研究
- 市场信号检测

---

## 二、API 接口

### 端点信息

| 项目 | 值 |
|------|------|
| 方法 | `POST` |
| 路径 | `/v1/chat/completions` |
| 完整 URL | `https://api.asksurf.ai/surf-ai/v1/chat/completions` |
| 认证 | `Authorization: Bearer <API_KEY>` |
| Content-Type | `application/json` |
| 非流式响应 | `application/json` |
| 流式响应 | `text/event-stream`（SSE） |

> ⚠️ **完全兼容 OpenAI Chat Completions 格式**，额外提供 `ability` 和 `citation` 扩展字段。

---

## 三、模型列表

### 旧版模型

| 模型 | 用途 | 建议超时 |
|------|------|----------|
| `surf-ask` | 快速问答 | 2分钟 |
| `surf-research` | 深度研究 | **10分钟** |

### 新版模型（推荐）

| 模型 | 用途 | 说明 |
|------|------|------|
| `surf-1.5-instant` | 快速响应 | 轻量级，适合简单查询 |
| `surf-1.5-thinking` | 深度推理 | 适合复杂多步分析 |
| `surf-1.5` | **自适应**（推荐） | 自动在 instant 和 thinking 间切换，建议超时 **10分钟** |

### surf-1.5 新特性

- **性能提升**：响应质量更高，instant 延迟显著降低
- **函数调用**：支持 `tools` 定义，可编排多步工具任务
- **推理深度可调**：通过 `reasoning_effort`（low/medium/high）控制
- **Agent 工作流**：支持 `ability`（能力域约束）和 `citation`（引用格式）

---

## 四、请求参数

### 必填参数

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `model` | string | 模型标识 | `"surf-1.5"` |
| `messages` | array | 消息列表 | `[{"role":"user","content":"..."}]` |

### 可选参数

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `stream` | boolean | 是否流式输出（默认 false） | `true` → SSE |
| `reasoning_effort` | string | 推理强度 | `"low"` / `"medium"` / `"high"` |
| `ability` | array | **Surf 扩展**：可用能力域 | 见下表 |
| `citation` | array | **Surf 扩展**：引用格式 | `["source", "chart"]` |
| `tools` | array | OpenAI 函数调用定义 | 见下方示例 |

### ability 能力域（关键！）

| 值 | 说明 | 适用场景 |
|----|------|----------|
| `search` | 网络搜索 | 新闻、公告、融资 |
| `evm_onchain` | EVM 链上数据 | TVL、交易量、持仓、ETH/BSC/Base 等 |
| `solana_onchain` | Solana 链上数据 | SOL 生态项目 |
| `market_analysis` | 市场分析 | 价格、技术指标、衍生品 |
| `calculate` | 计算 | 估值、收益率、倍数 |

### citation 引用格式

| 值 | 说明 |
|----|------|
| `source` | 数据来源引用 |
| `chart` | 图表引用 |

---

## 五、请求示例

```json
{
  "model": "surf-1.5",
  "messages": [
    {
      "role": "system",
      "content": "You are Surf, an analysis assistant focused on crypto markets and on-chain data."
    },
    {
      "role": "user",
      "content": "Analyze the Ethena (ENA) project: price, TVL, funding, risks."
    }
  ],
  "stream": false,
  "reasoning_effort": "medium",
  "ability": ["search", "evm_onchain", "market_analysis"],
  "citation": ["source"]
}
```

### cURL 示例

```bash
curl --request POST \
  --url https://api.asksurf.ai/surf-ai/v1/chat/completions \
  --header 'Authorization: Bearer sk-xxxx' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "surf-1.5-instant",
    "messages": [{"role": "user", "content": "Hyperliquid TVL and volume?"}],
    "stream": false,
    "reasoning_effort": "low",
    "ability": ["search", "market_analysis"],
    "citation": ["source"]
  }'
```

---

## 六、响应格式

### 非流式响应

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699890366,
  "model": "surf-ask",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "BTC is trading flat...",
        "reasoning": "（可选）模型推理过程"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 23,
    "completion_tokens": 12,
    "total_tokens": 35
  }
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 本次补全的唯一标识 |
| `choices[].finish_reason` | string | 结束原因：`stop`（正常）/ `length`（达限）/ `tool_calls`（触发工具）/ `error` |
| `choices[].message.content` | string | 模型输出文本 |
| `choices[].message.reasoning` | string | （可选）推理/思考过程 |
| `usage.prompt_tokens` | int | 输入 token 数 |
| `usage.completion_tokens` | int | 输出 token 数 |

### 流式响应（SSE）

`stream=true` 时，服务器持续推送 SSE 事件：

```
data: {"id":"...","choices":[{"delta":{"content":"部分内容"}}]}
data: {"id":"...","choices":[{"delta":{"content":"更多内容"}}]}
data: [DONE]
```

- 每个 chunk 的 `object` 为 `chat.completion.chunk`
- 增量内容通过 `choices[].delta`（role/content）传递
- `finish_reason` 在流结束前通常为 `null`
- 终止事件：`data: [DONE]`

---

## 七、错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| `400` | 请求参数错误 |
| `401` | 认证失败（API Key 无效或过期） |
| `502` | 服务端错误 |

错误响应格式：

```json
{
  "success": false,
  "message": "error description",
  "error_code": "FORBIDDEN"
}
```

---

## 八、我们的投研模式集成方案

### 推荐模型选择

| 场景 | 推荐模型 | reasoning_effort | 超时 |
|------|----------|-----------------|------|
| 快速项目概述 | `surf-1.5-instant` | `low` | 60s |
| 标准投研分析 | `surf-1.5` | `medium` | 5min |
| 深度研究报告 | `surf-research` | `high` | 10min |

### 推荐 ability 组合

| 分析类型 | ability 组合 |
|----------|-------------|
| 项目基本面 | `["search", "evm_onchain", "market_analysis"]` |
| 社交情绪 | `["search"]` |
| 链上数据 | `["evm_onchain"]` 或 `["solana_onchain"]` |
| 估值计算 | `["market_analysis", "calculate"]` |
| 全面分析 | `["search", "evm_onchain", "market_analysis", "calculate"]` |

### 连通测试结果（2026-02-25）

| 测试 | 模型 | 耗时 | 状态 |
|------|------|------|------|
| 快速问答 | `surf-ask` | ~42s | ✅ 200 |
| 投研查询 | `surf-1.5-instant` | ~33s | ✅ 200 |

> API Key 已存入 `backend/.env`（`SURF_API_KEY`）  
> 测试脚本：`backend/scripts/test_surf_api.py`
