# P11 数据管线与内容生产体系

> **版本**: v7.1  
> **日期**: 2026-01-22  
> **状态**: 📋 规划完成，待执行

---

## 🎯 核心目标

规范化数据清洗流程，建立统一前端管理界面，实现大规模内容生产。

---

## 🤖 模型配置

| 模型 | ID | 场景 |
|------|-----|------|
| **DeepSeek V3.2** | `deepseek-v3-2-251201` | ⭐ 数据清洗 (更便宜) |
| 豆包 Seed | `doubao-seed-1-8-251228` | 多模态/通用 |

---

## ⚠️ 8 大警告

### 批量推理坑
1. **TOS IAM 权限** - 配置 `TOSReadOnlyAccess` + `TOSWriteAccess`
2. **JSONL 格式** - `json.dumps()` 强校验
3. **Batch Endpoint** - 确认支持批量
4. **24h 窗口** - 前端显示 "1-24h"

### 质量杀手
A. **模型选型** - 用满血版非蒸馏版
B. **Prompt** - 必须 Few-Shot 示例
C. **Context** - 超 30k 切分
D. **Temperature** - = 0 无幻觉

---

## 📋 执行计划

| 阶段 | 任务 | 预估 |
|------|------|------|
| **Phase 0** | 10 条 Smoke Test | 1h |
| **Phase 1** | 统一数据导入器 | 4-5h |
| **Phase 2** | 前端管理页 `/cleaner` | 4-5h |
| **Phase 3** | 批量推理生产化 | 3-4h |

**总计**: 16-20h

---

## 📊 当前进度

| 任务 | 状态 |
|------|------|
| 问题诊断 | ✅ 完成 |
| 方案设计 | ✅ v7.1 |
| 模型配置文档 | ✅ 完成 |
| Phase 0 Smoke Test | ⏳ 待执行 |

---

## 🔗 相关文档

- [volcengine_models.md](file:///d:/AI_Projects/2026001/docs/volcengine_models.md) - 模型配置
- [PROJECT_HANDBOOK.md](file:///d:/AI_Projects/2026001/PROJECT_HANDBOOK.md) - 项目手册

---

*更新: 2026-01-22 13:00 夜班*
