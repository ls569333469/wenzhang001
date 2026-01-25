# Phase 4 Implementation Plan: Deep Research Integration

## Goal
Connect the React "Island Architecture" to the FastAPI `FastAPI` backend to enable real-time "Deep Research" article generation.

## 1. Technical Design

### 1.1 Store Architecture (`useAgentStore`)
We will create a specific Zustand store `src/features/agent/stores/useAgentStore.ts` to handle the streaming session.

**State:**
```typescript
interface AgentState {
  status: 'idle' | 'connecting' | 'streaming' | 'completed' | 'error';
  timeline: TimelineStep[]; // Mapped from backend nodes
  content: string; // The generated article text
  logs: string[]; // Raw logs
  
  // Actions
  startSession: (payload: GenerateRequest) => Promise<void>;
  stopSession: () => void;
}
```

### 1.2 SSE Event Mapping
We need to map backend events to frontend timeline states.

| Backend Node | Frontend Step ID | Visual Label |
| :--- | :--- | :--- |
| `node_strategist` | `step-strategy` | STRATEGIST |
| `node_writer` | `step-writer` | WRITER |
| `node_critic` | `step-critic` | CRITIC |
| `node_polisher` | `step-polisher` | POLISHER |

**Event Handling:**
- `thinking_step`: Updates the `message` of the CURRENT active step.
- `agent_update` (completed): Marks current step `status: 'completed'`, activates next step.
- `final_result`: Updates `content`.

## 2. Proposed Changes

### [NEW] `src/features/agent/stores/useAgentStore.ts`
- Implementation of the SSE client and state logic.
- Using `fetch-event-source` (or native `EventSource` with POST support, usually needs `fetch` adapter).
- *Decision*: Next.js native `fetch` reading `body.getReader()` is often robust for POST streaming. Or use `@microsoft/fetch-event-source`. Let's stick to native `fetch` + `TextDecoder` for zero dependencies if possible, or simple `eventsource-parser`.

### [MODIFY] `src/app/studio/page.tsx`
- Hydrate `ConfigIsland` with `startSession`.
- Hydrate `AgentIsland` with `steps` from store.
- Bind `WritingCanvas` (Center) to `content` from store.

### [MODIFY] `src/features/studio/components/layout/ConfigIsland.tsx`
- Add "Run Deep Research" button triggering `startSession`.

### [MODIFY] `src/features/studio/components/layout/AgentIsland.tsx`
- Remove Mock Data.
- Connect to `useAgentStore`.

## 3. Verification Plan

### 3.1 Unit Test (Manual)
- **Action**: Click "Run" in ConfigPanel.
- **Expectation**:
  1.  Timeline shows "Strategist" becoming Active.
  2.  "Thinking..." activity appears.
  3.  Steps progress sequentially.
  4.  Content appears in the center canvas.
  5.  No console errors.

### 3.2 E2E
- Since backend is running on `8002` (via proxy `Config`?), we must ensure `src/config/api.ts` points to correct backend URL.

## 4. Risks
- **CORS**: Backend allows `localhost:3000`, need to ensure we are on `3000` or `3001`.
- **Timeouts**: Long generation might timeout request. Backend has `asyncio.sleep` integration, frontend needs to handle open connection.
