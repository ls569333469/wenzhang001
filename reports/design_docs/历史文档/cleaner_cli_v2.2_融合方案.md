# cleaner_cli v2.2 融合方案

> **创建日期**: 2026-01-14  
> **状态**: 待审批  
> **目标**: 融合 v2.0 和 v2.1 的优点，打造最终工业级清洗工具

---

## 📊 版本能力矩阵

| 能力 | v2.0 当前版本 | v2.1 PRD | v2.2 融合版 |
|:-----|:------------:|:--------:|:-----------:|
| 异步并发 (AsyncIO) | ✅ | ❌ | ✅ |
| 断点续传 | ✅ | ❌ | ✅ |
| 本地 MD5 去重 | ✅ | ❌ | ✅ |
| Lark 服务端去重 | ✅ | ❌ | ✅ |
| API 限流重试 (tenacity) | ✅ | ❌ | ✅ |
| 智能规划器 (预扫描) | ⚠️ 部分 | ✅ | ✅ |
| 模块化架构 | ⚠️ 一般 | ✅ | ✅ |
| 多条提取 Prompt | ✅ | ⚠️ 简化 | ✅ |
| 真实 Lark 集成 | ✅ | ❌ Mock | ✅ |
| 进度条显示 | ✅ | ✅ | ✅ |

---

## 🎯 融合目标

### 从 v2.0 保留
1. **AsyncIO 异步架构** - 并发处理，速度快
2. **断点续传** - `processed_log.json`
3. **双重去重** - 本地 MD5 + Lark 端
4. **tenacity 重试** - API 稳定性
5. **多条提取 Prompt** - 高提取率
6. **真实 Lark 集成** - 实际入库

### 从 v2.1 吸收
1. **预扫描规划** - 启动前显示总分片数
2. **模块化架构** - 更清晰的代码结构
3. **LLMProvider 类** - 统一的模型工厂

---

## 🔧 具体变更

### 变更 1: 增加预扫描规划器

```python
# 新增函数：在 process_file 开始时调用
def plan_processing(file_path: Path, chunk_size: int = 3000):
    """预扫描文件，规划处理策略"""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    total_chars = len(text)
    estimated_chunks = math.ceil(total_chars / chunk_size)
    
    console.print(f"[bold cyan]🔍 预处理分析:[/bold cyan]")
    console.print(f"   📊 文件大小: {total_chars:,} 字符")
    console.print(f"   🔢 预计分片: {estimated_chunks} 块")
    console.print(f"   ⏱️ 预计耗时: {estimated_chunks * 3}~{estimated_chunks * 5} 秒")
    
    return text, estimated_chunks
```

### 变更 2: 重构 LLM 配置为类

```python
class AsyncLLMProvider:
    """v2.2 统一的异步 LLM 工厂"""
    
    PROVIDERS = {
        "doubao": {
            "env_key": "VOLC_API_KEY",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model_env": "VOLC_MODEL_ENDPOINT"
        },
        "deepseek": {
            "env_key": "DEEPSEEK_API_KEY",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat"
        },
        "gemini": {
            "env_key": "GOOGLE_API_KEY",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "model": "gemini-1.5-flash"
        }
    }
    
    def __init__(self, provider_name: str):
        self.name = provider_name
        self.config = self.PROVIDERS.get(provider_name)
        
    async def get_client(self) -> tuple[AsyncOpenAI, str]:
        # ... 返回 client 和 model_name
```

### 变更 3: 增强启动信息

```python
# 启动时显示完整规划
console.print(f"""
[bold green]🚀 P12.2 工业级清洗工具 v2.2[/bold green]
   📁 输入: {input_path}
   👤 作者: {author}
   🎨 风格: {style}
   🤖 模型: {provider}
   ⭐ 最低分: {min_score}
   🔄 并发数: {CONCURRENCY_LIMIT}
   📄 分片大小: {CHUNK_SIZE} 字符
   
[bold cyan]📊 预处理分析结果:[/bold cyan]
   📄 文件数量: {len(files)} 个
   🔢 总分片数: {total_chunks} 块
   ⏱️ 预计耗时: {estimated_time} 分钟
""")
```

---

## 📁 文件变更清单

| 文件 | 操作 | 说明 |
|:-----|:-----|:-----|
| `backend/tools/cleaner_cli.py` | 修改 | 增加预扫描、重构 LLM 类 |
| `backend/tools/processed_log.json` | 保留 | 断点续传 |

---

## 🧪 验收标准

| 项目 | 标准 |
|:-----|:-----|
| 大文件提取率 | >= 200 条 (957KB) |
| 完整性 | 100% 分片处理，无遗漏 |
| 速度 | 保持异步并发优势 |
| 稳定性 | 超时自动重试，断点可恢复 |

---

## ⏱️ 实施计划

| 阶段 | 任务 | 预计工时 |
|:-----|:-----|:--------:|
| Phase 1 | 增加预扫描规划器 | 15 min |
| Phase 2 | 重构 LLMProvider 类 | 20 min |
| Phase 3 | 增强启动信息显示 | 10 min |
| Phase 4 | 测试验证 | 15 min |

---

**请审批后开始实施**
