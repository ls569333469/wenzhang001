# Phase 4 Tasks: Deep Research Integration

- [ ] **4.1 API Contract Analysis**
  - [ ] Inspect `backend/app/main.py` for SSE endpoints.
  - [ ] Inspect `backend/app/graph.py` for event types (thinking/writing/done).
- [ ] **4.2 Frontend Data Layer**
  - [ ] Create `useAgentStore` (Zustand) for business logic.
  - [ ] Implement SSE Client (EventSource or fetch-based stream).
- [ ] **4.3 Component Wiring**
  - [ ] Connect `ConfigPanel` "Run" button to `useAgentStore.startSession()`.
  - [ ] Connect `AgentTimeline` to `useAgentStore.steps`.
  - [ ] Connect `WritingCanvas` to `useAgentStore.content`.
- [ ] **4.4 Verification**
  - [ ] E2E Test: Run a full generation cycle.
