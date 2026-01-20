# 🧠 Quantum Studio

> **AI 驱动的 Web3 投研内容创作引擎**
>
> 版本: v6.2 Stable | 架构: Next.js 16 + FastAPI + LangGraph

---

## ✨ 项目简介

Quantum Studio 是一款面向 Web3 领域的智能写作工坊，通过多智能体协作 (LangGraph) 与知识检索增强 (RAG)，自动生成专业级投研分析文章。

### 核心能力

| 模块 | 功能 | 状态 |
| :--- | :--- | :---: |
| **多智能体工作流** | 策略师 → 研究员 → 写作者 → 评审员 | ✅ |
| **知识库集成** | 飞书多维表格 (Lark) 自动同步 | ✅ |
| **流式输出** | SSE 实时展示 Agent 思考过程 | ✅ |
| **可视化工坊** | Paper Mode 极简 UI | ✅ |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 16)                │
│  ┌─────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │Dashboard│  │   Studio    │  │ Agent Inspector  │    │
│  │ (状态)  │  │ (三栏布局)  │  │   (实时日志)    │    │
│  └─────────┘  └─────────────┘  └──────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │ SSE / REST
┌────────────────────────▼────────────────────────────────┐
│                  Backend (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │ LangGraph│  │   RAG    │  │   Lark Connector   │    │
│  │ (Agents) │  │(ChromaDB)│  │   (知识库同步)     │    │
│  └──────────┘  └──────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Node.js 20+
- Python 3.11+
- pnpm / npm

### 1. 克隆项目

```bash
git clone https://github.com/ls569333469/wenzhang001.git
cd wenzhang001
```

### 2. 启动后端

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

打开浏览器访问 **http://localhost:3000**

---

## 📁 项目结构

```
wenzhang001/
├── frontend/                 # Next.js 16 前端
│   ├── src/
│   │   ├── app/(main)/       # 页面路由 (dashboard, studio, knowledge, settings)
│   │   ├── components/       # UI 组件库
│   │   │   ├── layout/       # 布局组件 (AppSidebar)
│   │   │   └── ui/           # 原子组件 (PaperCard, ActionTile)
│   │   └── features/         # 功能模块
│   │       └── workbench/    # Studio 核心 (WritingCanvas, AgentInspector)
│   └── tailwind.config.ts    # Design Tokens 配置
│
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── graph.py          # LangGraph 多智能体定义
│   │   ├── core/             # 核心服务 (Lark, LLM)
│   │   └── services/         # 业务逻辑
│   └── data/
│       └── prompts/          # Agent Prompt 模板 (Jinja2)
│
└── reports/                  # 设计文档与日志
    └── design_docs/          # 架构文档 (v6.2)
```

---

## 🎨 设计规范 (v6.2)

### Design Tokens

| Token | CSS Class | Value | 用途 |
| :--- | :--- | :--- | :--- |
| Paper | `bg-paper` | #F9F8F6 | 全站背景色 |
| Surface | `bg-surface` | #FFFFFF | 卡片容器 |
| Ink Primary | `text-ink-primary` | #27272A | 正文标题 |
| Ink Muted | `text-ink-muted` | #71717A | 辅助文字 |
| Hairline | `border-hairline` | #E4E4E7 | 分割线 |

### 组件规范

- **AppSidebar**: 全局单例侧边栏，280px 宽度
- **PaperCard**: 标准卡片容器，`bg-surface border-hairline`
- **ActionTile**: 交互式列表项，替代传统 Link

---

## 📋 开发进度

- [x] Phase 2: Dashboard 上线 + 系统状态监测
- [x] Phase 2: Design Lab & Tailwind v3 Fix
- [x] Phase 3: Studio - Island Architecture (Variant A) 实现
- [ ] Phase 4: 业务逻辑接入 (Deep Research Agent)
- [ ] Phase 4: Settings 系统设置页面

---

## 📄 License

MIT License © 2026

---

<p align="center">
  <b>Quantum Studio</b> — 用 AI 重新定义 Web3 投研写作
</p>
