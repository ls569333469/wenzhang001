# PROJECT_STATUS (Mnemosyne Protocol)

> **Last Updated**: 2026-01-06
> **Architecture**: Hybrid (Next.js 16 + FastAPI/Python)
> **Core Engine**: LangGraph + Google Gemini 3.0

## 1. Current State
- **Phase**: Initialization
- **Status**: Setting up project structure and environment.

## 2. Tech Stack Definition (Immutable)
- **Frontend**: Next.js 16, Tailwind CSS, Shadcn/UI (Cyberpunk Theme).
- **Backend API**: FastAPI (Python 3.12).
- **Agent Orchestrator**: LangGraph (Stateful).
- **Models**: 
  - Strategist/Critic/Writer: `gemini-3.0-pro-latest`
  - Router: `gemini-2.5-flash`

## 3. Style Rules (The Chronos Protocol)
1.  **Time Awareness**: All System Prompts MUST be injected with `current_time_iso`.
2.  **No AI Clichés**: Ban words: "delve", "tapestry", "landscape", "crucial", "testament".
3.  **Tone**: Aggressive, Insider, or Intimate. NEVER Generic.

## 4. Immediate Todo List
- [x] Create PROJECT_STATUS.md
- [ ] Initialize `/frontend` (Next.js).
- [ ] Initialize `/backend` (FastAPI).
- [ ] Create `mimeng_dataset_clean.txt`.
- [ ] Implement `backend/app/graph.py` (LangGraph Logic).
