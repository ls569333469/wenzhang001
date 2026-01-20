import { create } from 'zustand'
import { produce } from 'immer'
import { LucideIcon } from 'lucide-react'

// Types
export interface StrategyOption {
    id: string
    title: string
    hook_angle: string
    pain_point: string
    target_audience: string
    outline: string[]
}

export type Stage = 'input' | 'analyzing' | 'selection' | 'generating' | 'finished'

export interface Log {
    timestamp: string
    message: string
}

export interface AgentStep {
    id: string
    name: string
    status: 'idle' | 'active' | 'completed' | 'error'
    icon: LucideIcon
    logs: string[]
    thinkingSteps: { step: string; content: string }[]
    progress: number
}

interface WorkbenchState {
    // Core Data
    input: string
    mode: string
    selectionType: 'single' | 'combination'
    narrativeType: string
    references: string[]
    result: string
    options: StrategyOption[]

    // UI State
    stage: Stage
    loading: boolean
    logs: Log[]
    agentSteps: AgentStep[]

    // Layout State
    sidebarOpen: boolean
    inspectorOpen: boolean

    // Actions
    setInput: (txt: string) => void
    setMode: (mode: string) => void
    setSelectionType: (type: 'single' | 'combination') => void
    setNarrativeType: (type: string) => void
    setReferences: (refs: string[]) => void
    setStage: (stage: Stage) => void
    setLoading: (loading: boolean) => void
    setResult: (result: string) => void
    setOptions: (options: StrategyOption[]) => void

    // Log Actions
    addLog: (message: string) => void
    clearLogs: () => void

    // Agent Actions
    initAgents: (agents: AgentStep[]) => void
    updateAgentStatus: (agentId: string, status: AgentStep['status']) => void
    addAgentThinkingStep: (agentId: string, step: { step: string; content: string }) => void

    // Layout Actions
    toggleSidebar: () => void
    toggleInspector: () => void
}

export const useWorkbenchStore = create<WorkbenchState>((set) => ({
    // Initial State
    input: '',
    mode: 'mimeng',
    selectionType: 'single',
    narrativeType: 'project_review',
    references: [],
    result: '',
    options: [],

    stage: 'input',
    loading: false,
    logs: [],
    agentSteps: [],

    sidebarOpen: true,
    inspectorOpen: true,

    // Actions
    setInput: (input) => set({ input }),
    setMode: (mode) => set({ mode }),
    setSelectionType: (selectionType) => set({ selectionType }),
    setNarrativeType: (narrativeType) => set({ narrativeType }),
    setReferences: (references) => set({ references }),
    setStage: (stage) => set({ stage }),
    setLoading: (loading) => set({ loading }),
    setResult: (result) => set({ result }),
    setOptions: (options) => set({ options }),

    addLog: (message) => set((state) => ({
        logs: [...state.logs, { timestamp: new Date().toLocaleTimeString(), message }]
    })),
    clearLogs: () => set({ logs: [] }),

    initAgents: (agentSteps) => set({ agentSteps }),

    updateAgentStatus: (agentId, status) => set(produce((state: WorkbenchState) => {
        const agent = state.agentSteps.find(a => a.id === agentId)
        if (agent) {
            agent.status = status
            if (status === 'completed') agent.progress = 100
        }
    })),

    addAgentThinkingStep: (agentId, step) => set(produce((state: WorkbenchState) => {
        const agent = state.agentSteps.find(a => a.id === agentId)
        if (agent) {
            agent.thinkingSteps.push(step)
            agent.status = 'active'
        }
    })),

    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    toggleInspector: () => set((state) => ({ inspectorOpen: !state.inspectorOpen })),
}))
