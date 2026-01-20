# 🚑 Phase 5 Extended: 逻辑缝合与功能补全 (Logic Stitching & Gap Filling)

**Goal**: Fix critical data gaps where UI configuration is not being passed to the backend, and add missing feature entry points (Knowledge, Settings).

## User Review Required
> [!IMPORTANT]
> This plan addresses CRITICAL GAPS identified in the audit. Existing backend integration will be modified to support the full schema.

## Proposed Changes

### 1. Logic Stitching (Store & UI)

#### [MODIFY] [useAgentStore.ts](file:///d:/AI_Projects/2026001/frontend/src/features/agent/stores/useAgentStore.ts)
- **Import Schema**: Replace local `GenerateRequest` interface with `GenerateRequest` type from `../../studio/schema`.
- **Update Action**: Modify `startSession` to accept `GenerationConfig` (or full `GenerateRequest`).
- **Payload Construction**: Ensure `temperature`, `style`, `length` are included in the API call.

#### [MODIFY] [ConfigPanel.tsx](file:///d:/AI_Projects/2026001/frontend/src/features/studio/components/ConfigPanel.tsx)
- **StartButton**: Update to collect all state (`style`, `length`, `temp`, `mode`, `input`).
- **Pass Data**: Call `startSession` with the complete configuration object.

### 2. Knowledge Entry (Sidebar & Config)

#### [MODIFY] [AppSidebar.tsx](file:///d:/AI_Projects/2026001/frontend/src/components/layout/AppSidebar.tsx)
- Add "Knowledge Brain" navigation item (icon: `Database` or `Brain`).

#### [MODIFY] [ConfigPanel.tsx](file:///d:/AI_Projects/2026001/frontend/src/features/studio/components/ConfigPanel.tsx)
- Add `KnowledgeSelector` component (Multi-select for Knowledge Bases).
- Bind to local state or URL state (`knowledge_ids`).

### 3. System Settings (API Key)

#### [MODIFY] [actions.ts](file:///d:/AI_Projects/2026001/frontend/src/features/studio/actions.ts)
- Ensure backend/proxy respects a dynamically provided API Key (if applicable) or confirm it uses env vars safely. (Note: Frontend may just need to set user preference context).

## Verification Plan

### Automated Tests
- None existing for UI interactions.
- Will rely on manual verification via Network Tab.

### Manual Verification
1.  **Logic Stitching**:
    - Open Developer Tools -> Network.
    - Select "Professional", "Long", "Temp 0.9".
    - Click "Start Research".
    - **Expectation**: POST request to `/generate` contains `style: "professional"`, `length: "long"`, `temperature: 0.9`.

2.  **Knowledge Entry**:
    - Verify "Knowledge" button exists in Sidebar.
    - Verify `KnowledgeSelector` allows selecting items (mocked if necessary).
