# 🧠 Quantum Studio

> **AI 驱动的 Web3 爆款内容生成引擎**
>
> 版本: v6.3 Knowledge Optimized | 架构: Next.js 16 + FastAPI + LangGraph

---

## ✨ 项目简介

Quantum Studio 是一款面向 Web3 领域的智能写作工坊，通过多智能体协作 (LangGraph) 与知识检索增强 (RAG)，帮助用户快速生成高传播力的爆款投研文章。

### 核心能力

| 模块 | 功能 | 状态 |
| :--- | :--- | :---: |
| **多智能体工作流** | 策略师 → 写作者 → 评审员 → 润色师 | ✅ |
| **知识库集成** | 飞书多维表格 (Lark) 自动同步 | ✅ |
| **流式输出** | SSE 实时展示 Agent 思考过程 | ✅ |
| **Island 架构 UI** | Z-Stack 浮岛布局，沉浸式创作 | ✅ |
| **交互式选题** | Human-in-the-Loop 策略选择 | ✅ |
| **优化版入库** | 合并 LLM + 批量上传 + LLM 摘要 | ✅ NEW |

---

## 📊 项目评分

> **评估日期**: 2026-01-24 (基于全链路 E2E DOM 测试)

| 维度 | 得分 | 说明 |
|------|------|------|
| 功能完整性 | 8/10 | 核心创作流程已打通 |
| 技术稳定性 | 8/10 | Schema + 入库优化完成 |
| UI/UX 设计 | 7/10 | Island 架构实现 |
| 爆款生成能力 | 6/10 | ⭐ 核心提升方向 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 16)                │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Config      │  │   Canvas     │  │  Agent        │  │
│  │ Island      │  │   (创作区)   │  │  Timeline     │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ SSE / REST
┌────────────────────────▼────────────────────────────────┐
│                  Backend (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │ LangGraph│  │   RAG    │  │   Lark Connector   │    │
│  │ (4 Agents)│  │(ChromaDB)│  │   (知识库同步)     │    │
│  └──────────┘  └──────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Node.js 20+
- Python 3.11+
- pnpm / npm

### 1. 启动后端

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问应用

- 主页: http://localhost:3000
- Studio: http://localhost:3000/studio
- API 文档: http://localhost:8000/docs

---

## 🛠️ 数据清洗工具

### 优化版入库脚本 (A/B 测试)

```bash
cd backend

# 旧版 (兜底)
python -m scripts.ingest_knowledge --all --limit 10

# 新版 (推荐) - 50% 省费用，60% 省时间
python -m scripts.ingest_optimized --all --limit 10
```

### 优化特性

| 特性 | 说明 |
|------|------|
| 合并 LLM 调用 | 评分 + 实体 + 关键词 + 摘要 一次返回 |
| 批量 Lark 上传 | 500 条/批，减少 99% 网络开销 |
| 本地 Hash 缓存 | 查重速度提升 100 倍 |
| LLM 生成摘要 | 一句话核心观点 (30 字以内) |

---

## 📁 项目结构

```
wenzhang001/
├── frontend/                 # Next.js 16 前端
│   └── src/
│       ├── app/              # 页面路由 (dashboard, studio)
│       ├── components/       # UI 组件 (Island, Timeline)
│       └── features/         # 业务模块 (agent, studio)
│
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── main.py           # API 入口 (/analyze, /generate)
│       ├── graph.py          # LangGraph 工作流
│       └── agents/           # Agent 实现
│   └── scripts/
│       ├── ingest_knowledge.py   # 旧版入库脚本
│       ├── ingest_optimized.py   # 优化版入库脚本 ⭐
│       └── batch/                # 批量处理模块
│
├── reports/                  # 设计文档与日志
├── PROJECT_HANDBOOK.md       # 项目手册 (Single Source of Truth)
└── README.md                 # 本文件
```

---

## 📋 开发进度

- [x] Phase 1-4: 拆迁、地基、组件、逻辑接入
- [x] Phase 5-6: 界面体验修复与打磨
- [x] Phase 7-8: 深度系统验证与协同测试
- [x] Phase 9: 全链路 E2E 验证通过 ✅ (2026-01-21)
- [x] **Phase 10: Knowledge_Repo 优化** ✅ (2026-01-24)
  - 字段规范 v4 定稿
  - 优化版入库脚本 (A/B 测试)
  - LLM 生成一句话摘要
- [ ] Phase 11: 爆款核心能力增强

---

## 📄 License

MIT License © 2026

---

<p align="center">
  <b>Quantum Studio</b> — 用 AI 打造 Web3 爆款内容
</p>
