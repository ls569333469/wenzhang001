'use client';

import { create } from 'zustand';
import { API_BASE_URL } from '@/config/api';
import { TimelineStep } from '../../studio/components/timeline/AgentTimeline';
import { toast } from 'sonner';

// --- Types ---

import { type GenerateRequest, type CreationConfig, defaultConfig } from '../../studio/schema';

// Session Status Type
type SessionStatus = 'idle' | 'connecting' | 'thinking' | 'writing' | 'listening' | 'completed' | 'error';


interface AgentState {
    status: SessionStatus;
    error: string | null;
    steps: TimelineStep[];
    content: string;
    // Phase 6: Two-Stage Workflow State
    strategyOptions: any[] | null;
    analysisResult: {
        info_anchors: {
            must_mention: string[];
            key_data: string[];
            can_extend: string[];
        };
        style_notes: string;
    } | null;
    agentLogs: string[];
    isWaitingForSelection: boolean;
    // Phase 9: Store payload for confirmStrategy
    lastRequestPayload: { input: string; config: Partial<CreationConfig> } | null;

    // Actions
    startSession: (payload: { input: string, config: Partial<CreationConfig> }) => Promise<void>;
    confirmStrategy: (option: any) => Promise<void>; // Step 2 Trigger
    stopSession: () => void;
    resetSession: () => void;
}

// --- Initial Data ---
const INITIAL_STEPS: TimelineStep[] = [
    { id: 'step-strategy', agent: 'strategist', label: '策略分析', status: 'idle', message: '等待开始' },
    { id: 'step-writer', agent: 'writer', label: '初稿撰写', status: 'idle', message: '等待策略' },
    { id: 'step-critic', agent: 'critic', label: '质量审核', status: 'idle', message: '等待初稿' },
    { id: 'step-polisher', agent: 'polisher', label: '润色打磨', status: 'idle', message: '等待审核' },
];

/**
 * Phase 6 Helper: Inject Custom Prompts
 */
function injectPrompts(input: string): string {
    if (typeof window === 'undefined') return input;

    const pStrat = localStorage.getItem('qs_prompt_strategist');
    const pWriter = localStorage.getItem('qs_prompt_writer');
    const pCritic = localStorage.getItem('qs_prompt_critic');

    if (!pStrat && !pWriter && !pCritic) return input;

    let injection = "[SYSTEM OVERRIDE]\n";
    if (pStrat) injection += `Strategist: ${pStrat}\n\n`;
    if (pWriter) injection += `Writer: ${pWriter}\n\n`;
    if (pCritic) injection += `Critic: ${pCritic}\n\n`;

    injection += "[USER INPUT]\n";
    return injection + input;
}

// --- Store ---

export const useAgentStore = create<AgentState>((set, get) => ({
    status: 'idle',
    error: null,
    steps: INITIAL_STEPS,
    content: '',
    strategyOptions: null,
    analysisResult: null,
    agentLogs: [],
    isWaitingForSelection: false,
    lastRequestPayload: null,

    startSession: async ({ input, config }) => {
        // 1. Reset State
        set({
            status: 'connecting',
            error: null,
            content: '',
            steps: INITIAL_STEPS.map(s => ({ ...s, status: 'idle', message: '等待中...' })),
            strategyOptions: null,
            analysisResult: null,
            agentLogs: [],
            isWaitingForSelection: false,
            lastRequestPayload: { input, config }
        });

        // Activate Strategist
        const steps = get().steps;
        steps[0].status = 'active';
        steps[0].message = '正在连接量子引擎...';
        set({ steps: [...steps] });

        // Phase 6: Inject Prompts
        const finalInput = injectPrompts(input);

        try {
            // 2. Initiate Request to /analyze (Step 1)
            const requestBody: GenerateRequest = {
                prompt: finalInput,
                config: {
                    ...defaultConfig,
                    ...config
                }
            };

            // NOTE: Changing endpoint to /analyze
            const endpoint = `${API_BASE_URL}/analyze`;

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) throw new Error(`Failed to start analysis: ${response.statusText}`);
            if (!response.body) throw new Error("No response body received");

            set({ status: 'thinking' });

            // 3. Process Stream
            await processStream(response.body, set, get);

        } catch (err: unknown) {
            handleError(err, set, get);
        }
    },

    confirmStrategy: async (option: any) => {
        // Step 2: User selected an option, now call /generate
        set({ isWaitingForSelection: false, status: 'writing' });

        // Mark Strategist as Completed (if not already)
        const steps = get().steps;
        steps[0].status = 'completed';
        steps[0].message = '策略已确认';
        steps[1].status = 'active'; // Writer Start
        steps[1].message = '开始撰写...';
        set({ steps: [...steps] });

        try {
            // Phase 9 Fix: Use stored payload
            const { lastRequestPayload, analysisResult } = get();
            if (!lastRequestPayload) {
                throw new Error('No stored payload. Please start a new session.');
            }

            // Inject prompts again for /generate
            const finalInput = injectPrompts(lastRequestPayload.input);

            // Build request with selected_option
            const requestBody: GenerateRequest = {
                prompt: finalInput,
                config: {
                    ...defaultConfig,
                    ...lastRequestPayload.config
                },
                selected_option: option,
                info_anchors: analysisResult?.info_anchors
            };

            const response = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) throw new Error(`Failed to generate: ${response.statusText}`);
            if (!response.body) throw new Error('No response body received');

            // Process SSE stream (reuse existing helper)
            await processStream(response.body, set, get);

        } catch (err: unknown) {
            handleError(err, set, get);
        }
    },

    stopSession: () => {
        set({ status: 'idle' });
    },

    resetSession: () => {
        set({
            status: 'idle',
            error: null,
            steps: INITIAL_STEPS,
            content: '',
            strategyOptions: null,
            isWaitingForSelection: false
        });
    }
}));

// --- Helper: Stream Processor ---
// Extracting logic to support reuse
async function processStream(body: ReadableStream<Uint8Array>, set: any, get: any) {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const event = JSON.parse(line.slice(6));
                    handleEvent(event, set, get);
                } catch (e) { console.warn('SSE Parse Error', e); }
            }
        }
    }
}

function handleError(err: unknown, set: any, get: any) {
    const error = err as Error;
    console.error('Session Error:', error);
    set({ status: 'error', error: error.message || 'Unknown error' });
    toast.error(error.message || 'Unknown error');

    const steps = get().steps;
    const activeStep = steps.find((s: any) => s.status === 'active' || s.status === 'thinking');
    if (activeStep) {
        activeStep.status = 'error';
        activeStep.message = 'Process FAILED';
        set({ steps: [...steps] });
    }
}


// --- Event Handler ---
function handleEvent(event: BackendEvent, set: any, get: any) {
    const currentState = get();
    const steps = [...currentState.steps];

    switch (event.type) {
        case 'thinking_step': {
            const agentName = event.agent?.toLowerCase();
            const stepIndex = steps.findIndex(s => s.agent === agentName);
            if (stepIndex !== -1) {
                steps[stepIndex].status = 'thinking';
                steps[stepIndex].message = event.detail;
                set({ steps });
            }
            break;
        }
        case 'agent_update': {
            if (event.status === 'completed') {
                const agentName = event.step?.toLowerCase();
                const stepIndex = steps.findIndex(s => s.agent === agentName);
                if (stepIndex !== -1) {
                    steps[stepIndex].status = 'completed';
                    steps[stepIndex].message = 'Completed';

                    // Capture logs
                    if (event.logs && event.logs.length > 0) {
                        const newLogs = event.logs.map((l: string) => `[${agentName?.toUpperCase()}] ${l}`);
                        set({ agentLogs: [...get().agentLogs, ...newLogs] });

                        // Update message with last log if meaningful
                        const lastLog = event.logs[event.logs.length - 1];
                        if (lastLog) steps[stepIndex].message = lastLog;
                    }

                    // Auto-advance logic only if NOT Strategist (because Strategist waits for Selection)
                    if (agentName !== 'strategist' && stepIndex + 1 < steps.length) {
                        steps[stepIndex + 1].status = 'active';
                        steps[stepIndex + 1].message = 'Starting...';
                    }
                    set({ steps });
                }
            } else if (event.status === 'failed') {
                // Capture failure logs
                if (event.logs && event.logs.length > 0) {
                    const newLogs = event.logs.map((l: string) => `[${event.step?.toUpperCase()} ERROR] ${l}`);
                    set({ agentLogs: [...get().agentLogs, ...newLogs] });
                    toast.error(event.logs[0]);
                }
            }
            break;
        }
        case 'analysis_result': {
            // Phase 6 & 8: Receive Options AND Info Anchors
            const payload = event.payload; // { info_anchors, options, style_notes }
            if (payload && payload.options) {
                set({
                    strategyOptions: payload.options,
                    analysisResult: {
                        info_anchors: payload.info_anchors,
                        style_notes: payload.style_notes
                    },
                    isWaitingForSelection: true,
                    status: 'listening'
                });
                toast.success("Strategy Analysis Complete. Please Choose an Angle.");
            }
            break;
        }
        case 'final_result': {
            set({ content: event.payload, status: 'writing' });
            break;
        }
        case 'error': {
            set({ status: 'error', error: event.message });
            toast.error(event.message);
            break;
        }
        case 'end': {
            if (!currentState.isWaitingForSelection) {
                set({ status: 'completed' });
            }
            break;
        }
    }
}

// Types needed for compilation (re-declare or import if missing)
interface BackendEvent {
    type: 'thinking_step' | 'agent_update' | 'final_result' | 'error' | 'end' | 'analysis_result';
    agent?: string;
    step?: string;
    status?: string;
    detail?: string;
    payload?: any;
    message?: string;
    logs?: string[];
}
