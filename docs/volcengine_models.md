# 火山引擎模型配置指南

> **更新日期**: 2026-01-22  
> **API 端点**: `https://ark.cn-beijing.volces.com/api/v3`

---

## 推荐模型

| 模型 | ID | 输入价格 | 输出价格 | 推荐场景 |
|------|-----|----------|----------|----------|
| **DeepSeek V3.2** | `deepseek-v3-2-251201` | ¥0.002-0.004/千token | ¥0.003-0.006/千token | ⭐ **数据清洗** |
| 豆包 Seed | `doubao-seed-1-8-251228` | ¥0.0008-0.0024/千token | ¥0.002-0.024/千token | 多模态/通用 |

---

## 1. 豆包 Seed (doubao-seed-1-8-251228)

**特点**: 多模态理解，支持图片输入

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.getenv('ARK_API_KEY'),
)

# 文本任务
response = client.chat.completions.create(
    model="doubao-seed-1-8-251228",
    messages=[{"role": "user", "content": "你好"}],
    temperature=0,  # 清洗任务用 0
)

# 多模态任务 (图片理解)
response = client.responses.create(
    model="doubao-seed-1-8-251228",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_image", "image_url": "https://example.com/image.png"},
            {"type": "input_text", "text": "你看见了什么？"},
        ],
    }]
)
```

---

## 2. DeepSeek V3.2 (deepseek-v3-2-251201)

**特点**: 深度推理，支持联网搜索

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY')
)

# 基础调用
response = client.chat.completions.create(
    model="deepseek-v3-2-251201",
    messages=[{"role": "user", "content": "分析这篇文章"}],
    temperature=0,
)

# 联网搜索
tools = [{"type": "web_search", "max_keyword": 2}]
response = client.responses.create(
    model="deepseek-v3-2-251201",
    input=[{"role": "user", "content": "北京的天气怎么样？"}],
    tools=tools,
)
```

---

## 环境配置

```bash
# 安装
pip install --upgrade "openai>=1.0"

# 设置 API Key
export ARK_API_KEY=613f595c-0dc2-4753-b445-dc7ecff81a7b
```

---

## 数据清洗推荐配置

| 参数 | 值 | 说明 |
|------|-----|------|
| `model` | `doubao-seed-1-8-251228` | 成本最优 |
| `temperature` | `0` | 无幻觉 |
| `max_tokens` | `4096` | 足够输出 |

---

*最后更新: 2026-01-22 by 夜班*
