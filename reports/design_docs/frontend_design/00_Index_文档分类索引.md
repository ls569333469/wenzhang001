# Frontend Design 文档索引与分类

> **版本**: v1.0 | **更新日期**: 2026-01-25

---

## 📁 文档命名规范

```
[序号]-[子序号]_[类型]_[主题].md
```

| 类型代码 | 含义 | 示例 |
|----------|------|------|
| `Plan` | 规划方案 | 10-0_Plan_爆款能力升级.md |
| `Design` | 设计文档 | 3-1_Design_岛屿架构.md |
| `Task` | 任务清单 | 4-3_Task_逻辑接入.md |
| `Report` | 测试/分析报告 | 12-2_Report_Knowledge集成测试报告.md |
| `Summary` | 阶段总结 | 10-0_Summary_中场交付总结.md |
| `Manual` | 使用手册 | 12-3_Manual_Lark数据清洗工具手册.md |
| `Arch` | 架构图 | 14-1_Arch_数据清洗工具架构流程图.md |
| `Guide` | 指南 | 5-4_Guide_控制台检查.md |
| `Demo` | 演示文件 | 10-9_Demo_滑出面板.html |
| `Global` | 全局规范 | 00_Global_开发规范.md |
| `Walkthrough` | 交付演示 | 5-9_Walkthrough_扩展交付.md |
| `Delivery` | 交付物 | 6-3_Delivery_界面体验修复.md |
| `Issue_Log` | 问题日志 | 9-3_Issue_Log_全链路验证.md |
| `Analysis` | 分析文档 | 5-5_Analysis_差距分析.md |

---

## 📊 按主题分类

### 🔧 A. 数据清洗工具 (12-14)

> 核心主题：Lark 数据入库、Knowledge_Repo、数据清洗

| 序号 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| 12-1 | Plan_Knowledge集成.md | Plan | Strategist 集成 Knowledge_Repo |
| 12-2 | Report_Knowledge集成测试报告.md | Report | A/B 测试结果 |
| 12-3 | Manual_Lark数据清洗工具手册.md | **Manual** | ⭐ 核心手册 v7.0 |
| 13-1 | Plan_Web3批量清洗优化方案.md | Plan | 优化版入库方案 |
| 13-2 | Report_Knowledge字段调用流程分析.md | Report | 字段规范 v4 分析 |
| 14-1 | Arch_数据清洗工具架构流程图.md | **Arch** | ⭐ Mermaid 流程图 |

---

### 🚀 B. 爆款能力升级 (10)

> 核心主题：标题 AB 测试、爆款评分、Hook 设置、自适应布局

| 序号 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| 10-0 | Plan_爆款能力升级.md | Plan | P10 主计划 |
| 10-0 | Summary_中场交付总结.md | Summary | 阶段总结 |
| 10-7 | Design_新博主入库流程.md | Design | 风格库扩展 |
| 10-7 | Report_风格库健康报告.md | Report | 素材库状态 |
| 10-9 | Design_自适应布局.md | Design | A+ 方案设计 |
| 10-9 | Demo_最终布局.html | Demo | HTML 演示 |
| 10-9 | Demo_滑出面板.html | Demo | HTML 演示 |

---

### 📦 C. 数据管线 (11)

> 核心主题：企业级数据管线、批量推理、前端管理

| 序号 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| 11-0 | Plan_风格库完善与内容生产.md | Plan | P11 v7.1 主计划 |
| 11-1 | Report_P11技术交付报告.md | Report | 交付报告 |

---

### 🏝️ D. 前端架构 (3-6)

> 核心主题：Island 架构、逻辑接入、界面优化

| 序号 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| 3-1 | Design_岛屿架构.md | Design | Island 架构设计 |
| 3-2 | Demo_岛屿架构.md | Demo | 演示说明 |
| 4-1 | Plan_逻辑接入.md | Plan | 后端对接计划 |
| 4-2 | Design_逻辑接入.md | Design | 接入设计 |
| 4-3 | Task_逻辑接入.md | Task | 任务清单 |
| 4-4 | Summary_逻辑接入.md | Summary | 阶段总结 |
| 5-1 | Plan_打磨优化.md | Plan | UI/UX 优化 |
| 5-2 | Task_打磨优化.md | Task | 任务清单 |
| 5-4 | Guide_控制台检查.md | Guide | 调试指南 |
| 5-5 | Analysis_差距分析.md | Analysis | 问题分析 |
| 5-6 | Plan_扩展计划.md | Plan | 功能扩展 |
| 5-7 | Task_扩展任务.md | Task | 任务清单 |
| 5-9 | Walkthrough_扩展交付.md | Walkthrough | 交付演示 |
| 5-10 | Report_盲审差异.md | Report | 审查报告 |
| 5-11 | Plan_本地化对齐.md | Plan | 本地化 |
| 6-1 | Plan_界面体验修复.md | Plan | UX 修复 |
| 6-2 | Task_界面体验修复.md | Task | 任务清单 |
| 6-3 | Delivery_界面体验修复.md | Delivery | 交付物 |

---

### ✅ E. 测试验证 (7-9)

> 核心主题：E2E 测试、全链路验证、DOM 测试

| 序号 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| 7-1 | Report_深度系统验证.md | Report | 系统验证 |
| 8-1 | Plan_规模化测试.md | Plan | 压力测试 |
| 8-2 | Plan_深度协同测试.md | Plan | 协同测试 |
| 8-3 | Delivery_深度协同测试.md | Delivery | 交付物 |
| 9-1 | Plan_全链路验证.md | Plan | E2E 验证 |
| 9-2 | Task_全链路验证.md | Task | 任务清单 |
| 9-3 | Issue_Log_全链路验证.md | Issue_Log | 问题日志 |
| 9-4 | Report_DOM测试.md | Report | DOM 测试报告 |

---

### 📐 F. 全局规范 (00-02)

| 序号 | 文件名 | 类型 | 说明 |
|------|--------|------|------|
| 00 | Global_开发规范.md | Global | 开发规范 |
| 01 | Global_重构总计划.md | Global | 重构计划 |
| 02 | Global_设计规范_v2.1.md | Global | 设计规范 |

---

### 📝 G. 其他 / 待归档

| 文件名 | 建议处理 |
|--------|----------|
| 1-1_Summary_拆迁净化.md | 归档 → 历史文档 |
| 2-1_Summary_视觉验证.md | 归档 → 历史文档 |
| P5_打磨优化_扩展交付.md | 重命名 → 5-X_Delivery_xxx |
| lark优化方案.md | 合并至 12-3 或归档 |
| web3.md | 合并至 13-1 或归档 |

---

## 📁 建议目录结构

```
frontend_design/
├── 00_Global/                    # 全局规范
│   ├── 00_Global_开发规范.md
│   ├── 01_Global_重构总计划.md
│   └── 02_Global_设计规范_v2.1.md
│
├── A_数据清洗工具/               # 12-14 合并
│   ├── 12-1_Plan_Knowledge集成.md
│   ├── 12-2_Report_Knowledge集成测试报告.md
│   ├── 12-3_Manual_Lark数据清洗工具手册.md
│   ├── 13-1_Plan_Web3批量清洗优化方案.md
│   ├── 13-2_Report_Knowledge字段调用流程分析.md
│   └── 14-1_Arch_数据清洗工具架构流程图.md
│
├── B_爆款能力升级/               # 10 系列
│   └── ...
│
├── C_数据管线/                   # 11 系列
│   └── ...
│
├── D_前端架构/                   # 3-6 系列
│   └── ...
│
├── E_测试验证/                   # 7-9 系列
│   └── ...
│
├── images/                       # 图片资源
│
└── 历史文档/                     # 归档
    └── ...
```

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-01-25 | v1.0 | 初始版本：49 个文件分类索引 |
