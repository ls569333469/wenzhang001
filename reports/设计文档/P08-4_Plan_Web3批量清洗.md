# Web3 批量清洗优化方案 v4.0 (A/B 测试版)

> **创建日期**: 2026-01-24  
> **版本**: v4.0 (A/B 测试 + LLM 摘要)  
> **目标**: 优化 5,806 条 Web3 素材的清洗入库流程  
> **策略**: 保留旧脚本兜底，新脚本渐进验证  
> **v4.0 更新**: 新增 LLM 生成的一句话摘要，替代简单截取

---

## 一、A/B 测试架构

### 1.1 架构图

```
                     ┌─────────────────────────────────────┐
                     │   命令行参数 / Feature Flag          │
                     │   --use-optimized / user_config     │
                     └─────────────────┬───────────────────┘
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           ▼                                                       ▼
┌─────────────────────────┐                         ┌─────────────────────────┐
│    旧脚本 (A - 兜底)     │                         │   新脚本 (B - 优化版)    │
│ ingest_knowledge.py     │                         │ ingest_optimized.py     │
├─────────────────────────┤                         ├─────────────────────────┤
│ ✗ 2 次 LLM 调用/条      │                         │ ✓ 1 次 LLM 调用/条      │
│ ✗ 单条 Lark 上传        │                         │ ✓ 批量 Lark 上传        │
│ ✗ Lark API 查重         │                         │ ✓ 本地 Hash 缓存        │
├─────────────────────────┤                         ├─────────────────────────┤
│ 费用: ¥16 / 5806 条     │                         │ 费用: ¥8 / 5806 条      │
│ 时间: 5-6h              │                         │ 时间: 2h                │
│ 稳定性: ⭐⭐⭐⭐⭐         │                         │ 稳定性: ⭐⭐⭐ (待验证)   │
└─────────────────────────┘                         └─────────────────────────┘
```

### 1.2 文件结构

```
backend/scripts/
├── ingest_knowledge.py      # 旧脚本 (A - 兜底，不改动)
├── ingest_optimized.py      # 新脚本 (B - 优化版) [新增]
├── batch/                   # 批量处理工具 [新增目录]
│   ├── lark_batch.py        # Lark 批量上传封装
│   └── hash_cache.py        # 本地 Hash 缓存
└── ...
```

---

## 二、优化内容对比

| 优化项 | 旧脚本 (A) | 新脚本 (B) | 节省 |
|--------|-----------|-----------|------|
| LLM 调用 | 2 次/条 | 1 次/条 | 50% Token |
| Lark 上传 | 单条 | 批量 (500条/次) | 99% 网络时间 |
| 查重方式 | Lark API | 本地 Hash 缓存 | 99% 查重时间 |
| **总费用** | ¥16 | ¥8 | **50%** |
| **总时间** | 5-6h | 2h | **60%** |

---

## 三、详细执行计划

### Phase 1: 开发新脚本 (2h)

| Step | 任务 | 文件 | 预计时间 |
|------|------|------|----------|
| 1.1 | 添加 Lark 批量上传方法 | `lark_client.py` | 20min |
| 1.2 | 创建本地 Hash 缓存模块 | `batch/hash_cache.py` | 20min |
| 1.3 | 创建合并 LLM Prompt | `ingest_optimized.py` | 40min |
| 1.4 | 集成批量上传逻辑 | `ingest_optimized.py` | 30min |
| 1.5 | 添加 Feature Flag 支持 | `user_config.json` | 10min |

### Phase 2: 小批量测试 (1h)

| Step | 任务 | 验证点 |
|------|------|--------|
| 2.1 | 测试合并 Prompt | JSON 解析成功率 |
| 2.2 | 测试批量上传 | 500 条/批无报错 |
| 2.3 | 测试 Hash 缓存 | 重复记录正确跳过 |
| 2.4 | 对比新旧脚本 | 费用和时间差异 |

### Phase 3: 全量执行 (可选)

| 条件 | 操作 |
|------|------|
| Phase 2 成功 | 使用新脚本全量入库 |
| Phase 2 有问题 | 切回旧脚本兜底 |

---

## 四、新脚本核心代码设计

### 4.1 合并 LLM Prompt (v4.1 - 新增摘要)

```python
MERGED_PROMPT = """
分析以下 Web3 内容，返回 JSON:

标题: {title}
内容: {content[:2000]}
赛道: {topic}

返回格式 (严格 JSON，无其他文字):
{{
  "quality_score": 1-10,
  "summary": "一句话概括核心观点 (30字以内)",
  "entities": ["项目/人名/代币", ...],
  "keywords": ["关键词1", "关键词2", ...],
  "fact_type": "硬数据/深度分析/观点评论/梗_黑话/快讯资讯"
}}

评分标准:
- 信息密度(30%): 具体数据、项目名称、技术细节
- 时效性(20%): 最新事件或趋势
- 专业性(30%): 深度分析或独特见解
- 可读性(20%): 语言清晰流畅
"""
```

> 📌 **v4.1 更新**: 新增 `summary` 字段，由 LLM 生成一句话核心摘要，替代简单截取的前 500 字。

### 4.2 Lark 批量上传

```python
async def batch_upload_lark(records: list, batch_size=500):
    """批量上传到 Lark (每批最多 500 条)"""
    results = {"success": 0, "failed": 0}
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        payload = {"records": [{"fields": r} for r in batch]}
        
        try:
            resp = await lark_client.batch_create_records(app_token, table_id, payload)
            if resp.get("code") == 0:
                results["success"] += len(batch)
            else:
                results["failed"] += len(batch)
        except Exception as e:
            results["failed"] += len(batch)
            
    return results
```

### 4.3 本地 Hash 缓存

```python
class HashCache:
    def __init__(self, cache_file="processed_hashes.json"):
        self.cache_file = Path(cache_file)
        self.hashes = self._load()
    
    def _load(self):
        if self.cache_file.exists():
            return set(json.load(open(self.cache_file)))
        return set()
    
    def contains(self, content_hash: str) -> bool:
        return content_hash in self.hashes
    
    def add(self, content_hash: str):
        self.hashes.add(content_hash)
        
    def save(self):
        json.dump(list(self.hashes), open(self.cache_file, "w"))
```

---

## 五、切换方式

### 5.1 命令行切换

```bash
# 使用旧脚本 (兜底)
python -m scripts.ingest_knowledge --all --limit 10

# 使用新脚本 (优化版)
python -m scripts.ingest_optimized --all --limit 10
```

### 5.2 配置文件切换

```json
// config/user_config.json
{
  "feature_flags": {
    "use_knowledge_repo": true,
    "use_optimized_ingest": false  // true = 新脚本，false = 旧脚本
  }
}
```

---

## 六、风险与回滚

| 风险 | 概率 | 应对 |
|------|------|------|
| 合并 Prompt 解析失败 | 中 | 添加 JSON 修复逻辑 |
| 批量上传部分失败 | 低 | 记录失败记录，单条重试 |
| Hash 缓存损坏 | 低 | 重建缓存 |

### 回滚步骤

```bash
# 如果新脚本有问题，直接使用旧脚本
python -m scripts.ingest_knowledge --all
```

---

## 七、成功标准

| 指标 | 旧脚本 | 新脚本目标 | 验收 |
|------|--------|-----------|------|
| 费用 | ¥16 | ≤ ¥8 | 省 50%+ |
| 时间 | 5h | ≤ 2h | 省 60%+ |
| 成功率 | 91.5% | ≥ 95% | 稳定性提升 |
| 数据一致性 | 基准 | 100% 一致 | 无数据丢失 |

---

## 附录：相关文档

| 文档 | 用途 |
|------|------|
| [13-2_Report_Knowledge字段调用流程分析.md](file:///d:/AI_Projects/2026001/reports/design_docs/frontend_design/13-2_Report_Knowledge字段调用流程分析.md) | 字段调用分析 |
| [Web3数据清洗成本分析.md](file:///d:/AI_Projects/2026001/reports/design_docs/历史文档/Web3数据清洗成本分析.md) | 费用计算 |
| [12-3_Manual_Lark数据清洗工具手册.md](file:///d:/AI_Projects/2026001/reports/design_docs/frontend_design/12-3_Manual_Lark数据清洗工具手册.md) | 工具说明 |
