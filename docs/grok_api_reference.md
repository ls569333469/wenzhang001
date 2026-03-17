# Grok (xAI) API 完整开发者文档

> 来源: [docs.x.ai](https://docs.x.ai/developers/introduction) | 整理时间: 2026-03-16

---

## 目录

1. [概述与入门](#1-概述与入门)
2. [模型列表与定价](#2-模型列表与定价)
3. [Chat Completions API](#3-chat-completions-api)
4. [Responses API (工具调用)](#4-responses-api)
5. [Web Search 工具](#5-web-search)
6. [X Search 工具](#6-x-search)
7. [Code Execution 工具](#7-code-execution)
8. [Function Calling 自定义工具](#8-function-calling)
9. [Collections Search (RAG)](#9-collections-search)
10. [Remote MCP Tools](#10-remote-mcp)
11. [Files API 文件上传](#11-files-api)
12. [Citations 引用来源](#12-citations)
13. [消耗与限流](#13-消耗与限流)
14. [图片生成](#14-图片生成)
15. [项目集成参考](#15-项目集成参考)

---

## 1. 概述与入门

Grok 是 xAI 开发的大语言模型家族，灵感来自《银河系漫游指南》。

- **API 基地址**: `https://api.x.ai/v1`
- **认证**: `Authorization: Bearer $XAI_API_KEY`
- **SDK 支持**: OpenAI Python SDK、xAI 原生 Python SDK (`xai-sdk`)、OpenAI Node.js SDK、Vercel AI SDK (`@ai-sdk/xai`)
- **控制台**: [console.x.ai](https://console.x.ai)

### 快速开始

```bash
pip install openai
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Chat Completions (传统对话)
response = client.chat.completions.create(
    model="grok-4.20-beta-latest",
    messages=[
        {"role": "system", "content": "You are Grok."},
        {"role": "user", "content": "What is the meaning of life?"},
    ],
)
print(response.choices[0].message.content)

# Responses API (带工具调用)
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "xAI 最新动态"}],
    tools=[{"type": "web_search"}, {"type": "x_search"}],
)
print(response.output_text)
```

### 两种 API 对比

| 特性 | Chat Completions | Responses API |
|------|-----------------|---------------|
| 端点 | `POST /v1/chat/completions` | `POST /v1/responses` |
| Server-side Tools | ❌ 不支持 | ✅ web_search, x_search, code_interpreter 等 |
| 实时搜索 | ❌ 仅训练数据 | ✅ 实时搜索 X/Twitter + 全网 |
| 引用来源 | ❌ | ✅ 自动带 citations |
| Function Calling | ✅ | ✅ |
| 流式输出 | ✅ | ✅ |

> ⚠️ **Grok 知识截止约 2024 年 11 月**。不启用搜索工具时，无法获取实时信息。

---

## 2. 模型列表与定价

### 可用模型

| 模型 ID | 类型 | 上下文 | 输入/输出能力 | 价格 (per 1M tokens) |
|---------|------|--------|-------------|---------------------|
| `grok-4.20-beta-latest` | 推理旗舰 | 2M | text+image → text | 见控制台 |
| `grok-4.20-beta-latest-non-reasoning` | 非推理旗舰 | 2M | text+image → text | 见控制台 |
| `grok-4-0709` | 旗舰 | 256K | text+image → text+image | $3 / $15 |
| `grok-4-fast-reasoning` | 快速推理 | 2M | text+image → text | 见控制台 |
| `grok-4-fast-non-reasoning` | 快速非推理 | 2M | text+image → text | 见控制台 |
| `grok-4-1-fast-reasoning` | 4.1 快速推理 | 2M | text+image → text | $0.20 / $0.50 |
| `grok-4-1-fast-non-reasoning` | 4.1 快速非推理 | 2M | text+image → text | 类似 |
| `grok-3` | 标准 | 131K | text+image → text | $3 / $15 |
| `grok-3-mini` | 轻量 | 131K | text → text | $0.30 / $0.50 |

### 模型别名规则

- `grok-4.20-beta` → 最新稳定版
- `grok-4.20-beta-latest` → 最新版本（含 beta）
- `grok-4.20-beta-MMDD` → 日期锁定版本

### 重要注意

- **推理模型**（含 `reasoning`）：不支持 `presencePenalty`, `frequencyPenalty`, `stop`, `reasoning_effort` 参数
- **非推理模型**（含 `non-reasoning`）：**Live Search / 工具调用推荐使用此类型**，速度更快
- **图片输入**：最大 20MiB，支持 jpg/png，图片 token 消耗 256~1792 tokens
- **缓存**：自动启用，重复 prompt 享受缓存价格（约 50% 折扣）。可设置 `x-grok-conv-id` header 提高缓存命中率

### 工具调用定价

| 工具 | 计费方式 |
|------|---------|
| `web_search` | 按调用次数 |
| `x_search` | 按调用次数 |
| `code_interpreter` / `code_execution` | 按调用次数 |
| `collections_search` / `file_search` | 按调用次数 |
| `attachment_search` | 按调用次数 |
| `view_image` | 仅收 image token 费 |
| `view_x_video` | 仅收 image token 费 |
| Remote MCP | 仅收 token 费 |
| Function Calling | 仅收 token 费 |

---

## 3. Chat Completions API

兼容 OpenAI SDK 的标准聊天接口，**不支持 Server-side Tools**。

```python
response = client.chat.completions.create(
    model="grok-4.20-beta-latest",
    messages=[
        {"role": "system", "content": "你是投研助手"},
        {"role": "user", "content": "分析 Polymarket 项目"},
    ],
    temperature=0.7,
    max_tokens=4096,
    stream=False,
)
print(response.choices[0].message.content)
```

### 支持的参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | str | 模型 ID |
| `messages` | list | 对话历史 `[{role, content}]` |
| `temperature` | float | 0-2，控制随机性 |
| `max_tokens` | int | 最大输出 token |
| `stream` | bool | 是否流式输出 |
| `response_format` | dict | 结构化输出 `{"type": "json_object"}` |
| `top_p` | float | nucleus sampling |
| `n` | int | 生成多少个候选 |

### 图片输入 (Vision)

```python
response = client.chat.completions.create(
    model="grok-4.20-beta-latest",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64,<base64_string>",
                    "detail": "high"
                }
            },
            {"type": "text", "text": "描述这张图片"}
        ]
    }],
)
```

---

## 4. Responses API

支持 Server-side Tools 的新一代 API，所有工具通过此接口使用。

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "system", "content": "你是投研助手"},
        {"role": "user", "content": "搜索最新 Crypto 热门项目"},
    ],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
        {"type": "code_interpreter"},
    ],
    temperature=0.3,
    stream=False,
)

# 提取文本
print(response.output_text)

# 获取引用来源
print(response.citations)
```

### 工作流程

1. **分析查询** — 判断需要什么信息
2. **选择工具** — 决定调用哪些工具或直接回答
3. **执行工具** — 内置工具在 xAI 服务器端执行
4. **迭代处理** — 可能多次调用不同工具收集足够信息
5. **返回结果** — 附带引用来源 (citations)

### 响应结构

```python
response.output_text    # str: 最终文本输出
response.output         # list: 输出项列表
response.citations      # list[str]: 引用 URL 列表

# output 中每个 item
for item in response.output:
    item.type      # "message" | "web_search_call" | "function_call" 等
    item.role      # "assistant"
    item.status    # "completed"
    item.content   # list[{type, text}]
```

---

## 5. Web Search

搜索全网并浏览网页，获取实时信息。

### 基本用法

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Polymarket 最新融资情况"}],
    tools=[{"type": "web_search"}],
)
print(response.output_text)  # 带引用链接的实时数据
```

### 全部参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | str | 固定 `"web_search"` |
| `allowed_domains` | list[str] | 只搜索指定域名 |
| `excluded_domains` | list[str] | 排除指定域名 |
| `enable_image_understanding` | bool | 分析搜索结果中的图片 |

### 限定域名搜索

```python
tools=[{
    "type": "web_search",
    "allowed_domains": ["coindesk.com", "coingecko.com", "defillama.com"],
}]
```

### 排除域名

```python
tools=[{
    "type": "web_search",
    "excluded_domains": ["reddit.com", "medium.com"],
}]
```

### 启用图片理解

```python
tools=[{
    "type": "web_search",
    "enable_image_understanding": True,
}]
```

---

## 6. X Search

搜索 X/Twitter 帖子、用户资料和话题。**对投研项目最有价值的工具。**

### 基本用法

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "What are people saying about Polymarket on X?"}],
    tools=[{"type": "x_search"}],
)
```

### 全部参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | str | 固定 `"x_search"` |
| `allowed_x_handles` | list[str] | 只搜索指定账号帖子 (**最多 10 个**) |
| `excluded_x_handles` | list[str] | 排除指定账号 (**最多 10 个**) |
| `from_date` | str | 搜索起始日期 (ISO8601: `"YYYY-MM-DD"`) |
| `to_date` | str | 搜索结束日期 (ISO8601: `"YYYY-MM-DD"`) |
| `enable_image_understanding` | bool | 分析帖子中的图片 |
| `enable_video_understanding` | bool | 分析帖子中的视频 (**仅 X Search**) |

> ⚠️ `allowed_x_handles` 和 `excluded_x_handles` **不能同时使用**

### 指定账号搜索

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "xAI 的最新动态"}],
    tools=[{
        "type": "x_search",
        "allowed_x_handles": ["elonmusk"],
    }],
)
```

### 日期范围搜索

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "xAI 最近动态"}],
    tools=[{
        "type": "x_search",
        "from_date": "2025-10-01",
        "to_date": "2025-10-10",
    }],
)
```

### 启用图片+视频理解

```python
tools=[{
    "type": "x_search",
    "enable_image_understanding": True,
    "enable_video_understanding": True,
}]
```

### 排除账号

```python
tools=[{
    "type": "x_search",
    "excluded_x_handles": ["spam_bot_1", "spam_bot_2"],
}]
```

### 投研场景示例 — 搜索 KOL 推文

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{
        "role": "user",
        "content": "搜索以下 KOL 最近提到的热门 Crypto 项目，输出表格",
    }],
    tools=[{
        "type": "x_search",
        "allowed_x_handles": [
            "leakmealpha", "top7ico", "Eli5defi",
            "Web3Alerts", "WY_mask",
        ],
    }],
)
```

---

## 7. Code Execution

在 xAI 服务器端沙盒环境中执行 Python 代码。

### 基本用法

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "计算复利: 本金$10000, 年利率8%, 20年后是多少?"}],
    tools=[{"type": "code_interpreter"}],
)
```

> SDK 命名差异: xAI SDK 用 `code_execution`，OpenAI SDK 用 `code_interpreter`

### 适用场景

- **数学计算**: 复杂方程、统计分析、精确数值计算
- **数据分析**: 处理数据集、提取洞察
- **金融建模**: 投资回报、风险指标、量化分析
- **科学计算**: 模拟、数据转换
- **代码验证**: 编写、测试、调试 Python 代码

### 最佳实践

1. **具体请求**: "计算 xyz" 比 "帮我分析" 效果更好
2. **提供数据格式**: 告诉模型输入数据的结构
3. **适当 temperature**: 计算任务建议 `temperature=0`

---

## 8. Function Calling

自定义工具，模型决定何时调用，你在客户端控制执行。

### 定义工具

```python
tools = [{
    "type": "function",
    "name": "get_token_price",
    "description": "获取加密货币实时价格",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "代币符号，如 BTC, ETH"
            },
            "currency": {
                "type": "string",
                "enum": ["usd", "cny"],
                "default": "usd"
            },
        },
        "required": ["symbol"],
    },
}]
```

### 处理工具调用

```python
import json

response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "BTC 现在多少钱?"}],
    tools=tools,
)

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        # 执行你的函数
        result = get_token_price(args["symbol"])
        # 将结果返回给模型继续生成
```

### 与内置工具混合使用

```python
tools = [
    {"type": "web_search"},           # 内置: xAI 服务器端执行
    {"type": "x_search"},             # 内置: xAI 服务器端执行
    {                                 # 自定义: 客户端执行
        "type": "function",
        "name": "save_to_database",
        "description": "保存研究结果到数据库",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "要保存的数据"}
            },
            "required": ["data"],
        },
    },
]
```

混合使用时:
- **内置工具** — xAI 服务器自动执行
- **自定义工具** — 暂停执行，返回给你处理

### tool_choice 控制

| 值 | 说明 |
|----|------|
| `"auto"` | 模型自主决定（默认） |
| `"required"` | 必须调用至少一个工具 |
| `"none"` | 不使用任何工具 |
| `{"type": "function", "function": {"name": "xxx"}}` | 强制使用指定工具 |

### 并行工具调用

默认启用，模型可以一次返回多个 tool_call:

```python
for tool_call in response.tool_calls:
    result = tools_map[tool_call.function.name](
        **json.loads(tool_call.function.arguments)
    )
    # 追加每个结果...
```

禁用: 设置 `parallel_tool_calls: false`

---

## 9. Collections Search

RAG 文档检索工具 — 搜索你上传的文档集合。

### 适用场景

- **企业知识库**: AI 参考内部文档和政策
- **金融分析**: 分析 SEC 文件、财报
- **客服系统**: 基于产品文档回答问题
- **研究调查**: 综合多个学术论文和报告
- **合规法务**: 基于官方指南回答

### 基本用法 (OpenAI SDK)

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "Tesla Q4 2024 营收是多少?"}],
    tools=[{
        "type": "collections_search",
        "collection_ids": ["col_xxx"],  # 你创建的集合 ID
    }],
)
```

> SDK 命名差异: OpenAI SDK 也支持 `file_search` 作为别名

### 完整流程 (xAI SDK)

```python
from xai_sdk import AsyncClient
from xai_sdk.tools import collections_search, code_execution

client = AsyncClient(api_key="...", management_api_key="...")

# 1. 创建集合
collection = await client.collections.create("financial-reports")

# 2. 上传文档
await client.collections.upload_document(
    collection_id=collection.collection_id,
    name="report.pdf",
    data=pdf_bytes,
)
# 等待处理完成...

# 3. 搜索 + 分析
chat = client.chat.create(
    model="grok-4.20-beta-latest-non-reasoning",
    tools=[
        collections_search(collection_ids=[collection.collection_id]),
        code_execution(),  # 可选: 让模型做计算
    ],
)
```

### 与 Web/X Search 混合使用

```python
tools = [
    {"type": "collections_search", "collection_ids": ["col_xxx"]},
    {"type": "web_search"},
    {"type": "x_search"},
]
# → 内部文档 + 公开网络 + X/Twitter 三路检索
```

---

## 10. Remote MCP

连接远程 MCP (Model Context Protocol) 服务器，扩展 AI 能力。

### 基本用法

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "分析这个 GitHub 仓库"}],
    tools=[{
        "type": "mcp",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "server_label": "deepwiki",
    }],
)
```

### 配置参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | str | 固定 `"mcp"` |
| `server_url` | str | MCP 服务器 URL |
| `server_label` | str | 服务器标签（显示用） |
| `server_description` | str | 服务器描述 |
| `allowed_tool_names` | list[str] | 只允许使用指定工具 |
| `authorization` | str | 认证信息 |
| `extra_headers` | dict | 额外请求头 |

### 多服务器支持

```python
tools = [
    {"type": "mcp", "server_url": "https://mcp-server-1.com/mcp", "server_label": "server1"},
    {"type": "mcp", "server_url": "https://mcp-server-2.com/mcp", "server_label": "server2"},
]
```

> 注意: `require_approval` 和 `connector_id` 参数目前不支持

---

## 11. Files API

上传文件并在对话中使用。

### 工作原理

上传文件到消息后，API 自动启用 `attachment_search` Server-side Tool:
1. 自动变为 Agentic 请求
2. 模型自动搜索文档、提取信息
3. 支持多文件跨文档搜索

### 快速示例 (xAI SDK)

```python
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key="...")

# 1. 上传文档
uploaded = client.files.upload(b"Q4 Revenue: $5.2M", filename="report.txt")

# 2. 带文件对话
chat = client.chat.create(model="grok-4-fast")
chat.append(user("总营收是多少?", file(uploaded.id)))

# 3. 获取答案
response = chat.sample()
print(response.content)  # "总营收是 $5.2M"

# 4. 清理
client.files.delete(uploaded.id)
```

### 特性

- **多文件**: 一条消息可附加多个文件
- **多轮对话**: 后续消息可继续引用之前上传的文件
- **Code Execution 集成**: 可与代码执行工具配合分析文件数据
- **支持格式**: PDF, TXT, CSV 等

---

## 12. Citations

工具搜索结果自动带引用来源。

### 全量引用

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[{"role": "user", "content": "xAI 最新进展"}],
    tools=[{"type": "web_search"}],
)

# 所有搜索过程中遇到的 URL（可能包含未直接引用的）
print(response.citations)
# ['https://x.com/...', 'https://x.ai/news', ...]
```

### 内联引用

默认在文本中以 markdown 格式嵌入:

```
Polymarket获得CFTC批准[[1]](https://coindesk.com/...)，
估值达$9B[[2]](https://yahoo.com/...)。
```

### 禁用内联引用

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[...],
    tools=[{"type": "web_search"}],
    include=["citations.none"],
)
```

### 结构化引用数据

响应对象中包含精确的位置信息，可用于前端渲染引用标记。

---

## 13. 消耗与限流

### Token 类型

| Token 类型 | 说明 | 计费 |
|-----------|------|------|
| Input tokens | 你的查询和对话历史 | 输入价格 |
| Completion tokens | 模型最终回复 | 输出价格 |
| Reasoning tokens | 推理模型的思考过程 | 与输出价格相同 |
| Cached prompt tokens | 缓存命中的输入 | ~50% 折扣 |
| Image tokens | 图片分析 (256~1792 per image) | 输入价格 |

### 提高缓存命中率

```http
x-grok-conv-id: <固定的 uuid4>
```

在 HTTP header 中设置固定的 `x-grok-conv-id`，后续使用相同 header 的请求更容易命中缓存。

### 限流层级

层级基于 **自 2026-01-01 起的累计消费额** 自动升级:

- 达到消费阈值后自动升级
- 层级永不降级
- 每个层级有不同的 RPM (请求/分钟) 和 TPM (token/分钟) 限制
- 超限返回 HTTP `429` 错误

具体限制查看: [console.x.ai/team/default/rate-limits](https://console.x.ai/team/default/rate-limits)

### 查看 Token 消耗

```python
# 每个响应都有 usage 对象
print(response.usage)
```

```json
{
  "prompt_tokens": 199,
  "completion_tokens": 1,
  "total_tokens": 200,
  "prompt_tokens_details": {
    "text_tokens": 199,
    "image_tokens": 0,
    "cached_tokens": 163
  },
  "completion_tokens_details": {
    "reasoning_tokens": 0
  },
  "cost_in_usd_ticks": 158500
}
```

> `cost_in_usd_ticks` 单位: 1/10,000,000,000 美元

---

## 14. 图片生成

```python
response = client.images.generate(
    model="grok-4",
    prompt="A cat in a tree",
    n=4,
)
```

使用 Aurora 引擎，支持 `grok-4` 模型。

---

## 15. 项目集成参考

### 当前集成 (`llm.py`)

```python
# Grok Live Search (Responses API + web_search)
if provider == "grok" and extra_body.get("search"):
    search_model = "grok-4.20-beta-latest-non-reasoning"
    response = client.responses.create(
        model=search_model,
        input=messages,
        tools=[{"type": "web_search"}],
        temperature=temperature,
    )
    return response.output_text

# Grok 普通对话 (Chat Completions)
response = client.chat.completions.create(
    model="grok-4.20-beta-latest",
    messages=messages,
    temperature=temperature,
)
return response.choices[0].message.content
```

### 调用方式

```python
# 启用 Live Search
generate_text(prompt=..., provider="grok", extra_body={"search": True})

# 普通对话（无搜索）
generate_text(prompt=..., provider="grok")
```

### 🔮 可优化方向

| 优化项 | 当前 | 建议 | 效果 |
|--------|------|------|------|
| 侦察官搜索 | `web_search` | `x_search` + `allowed_x_handles` | 精准搜 KOL 推文 |
| 日期控制 | prompt 文字描述 | `from_date` / `to_date` 参数 | API 层面精确日期范围 |
| 图片分析 | 不支持 | `enable_image_understanding` | 分析 KOL 推文截图 |
| 视频分析 | 不支持 | `enable_video_understanding` | 分析推文视频内容 |
| RAG | 不支持 | `collections_search` | 搜索历史投研报告 |
| 成本控制 | 无 | `x-grok-conv-id` header | 提高缓存命中，降本 |

---

> 完整 API Reference: [docs.x.ai/developers/rest-api-reference](https://docs.x.ai/developers/rest-api-reference)
> 控制台: [console.x.ai](https://console.x.ai)
> 定价详情: [docs.x.ai/docs/models](https://docs.x.ai/docs/models)
