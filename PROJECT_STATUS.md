# PROJECT_STATUS (Mnemosyne Protocol)

> **Last Updated**: 2026-02-13
> **Architecture**: Hybrid (Next.js 16 + FastAPI/Python)
> **Core Engine**: LangGraph + Volcengine (豆包 Seed / DeepSeek V3.2)

## 1. Current State
- **Phase**: P24 — 全模式独立管线
- **Status**: P24 A/B/C 完成 (Critic/Polisher 模板独立化 + 创作重置)，P24-D (一致性补全) 待实施
- **Git Branch**: `feature/p10-workflow-refactor` (main 待合并)

## 2. Tech Stack Definition (Immutable)
- **Frontend**: Next.js 16, Tailwind CSS, Shadcn/UI, TipTap 富文本编辑器
- **Backend API**: FastAPI (Python 3.12)
- **Agent Orchestrator**: LangGraph (Stateful, 4-Agent Pipeline)
- **Models**: Volcengine (doubao-seed / deepseek-v3.2)
- **Data Source**: Google Sheets (风格样本 + 知识库 + 素材池)

## 3. Style Rules (The Chronos Protocol)
1. **Time Awareness**: All System Prompts MUST be injected with `current_time_iso`.
2. **No AI Clichés**: 250+ 禁用词库 (`forbidden_patterns.yaml`) 自动注入所有 Agent.
3. **Tone**: Aggressive, Insider, or Intimate. NEVER Generic.

## 4. Immediate Todo List
- [x] P24-A: Critic/Polisher 模板独立化 (5+4 per-mode 模板)
- [x] P24-B: per-mode 模型配置
- [x] P24-C: 创作重置功能 (新建创作按钮)
- [ ] P24-D: 一致性补全 (4智能体×6模式前端统一)
- [ ] Git: 提交未提交变更 + 合并 feature 到 main
- [ ] 短篇提示词定稿 (开头/结尾组合)
