'use client';

import { create } from 'zustand';
import { API_BASE_URL } from '@/config/api';
import { TimelineStep } from '../../studio/components/timeline/AgentTimeline';
import { toast } from 'sonner';
import { useAgentModelStore } from './useAgentModelStore';
import { useModeWriterStore } from './useModeWriterStore';

// --- Types ---

import { type GenerateRequest, type CreationConfig, defaultConfig } from '../../studio/schema';

// Session Status Type
type SessionStatus = 'idle' | 'connecting' | 'thinking' | 'writing' | 'listening' | 'completed' | 'error';

// P10-9: Studio Phase for adaptive layout
export type StudioPhase = 'idle' | 'thinking' | 'generating' | 'reading';

/**
 * P10-9: Map session status to layout phase
 */
export function mapStatusToPhase(status: SessionStatus): StudioPhase {
    switch (status) {
        case 'idle':
            return 'idle';
        case 'connecting':
        case 'thinking':
        case 'listening':
            return 'thinking';
        case 'writing':
            return 'generating';
        case 'completed':
            return 'reading';
        case 'error':
            return 'reading'; // Show result even on error
        default:
            return 'idle';
    }
}

// P13: 获取 API 配置 (从 localStorage)
function getAPIConfig() {
    if (typeof window === 'undefined') return undefined;
    try {
        const stored = localStorage.getItem('qs_api_config');
        return stored ? JSON.parse(stored) : undefined;
    } catch {
        return undefined;
    }
}

// P13: 获取 Agent 配置 (从 localStorage)
function getAgentConfig() {
    if (typeof window === 'undefined') return undefined;
    try {
        const stored = localStorage.getItem('qs_agent_config');
        return stored ? JSON.parse(stored) : undefined;
    } catch {
        return undefined;
    }
}


// P10-1: Title Candidate Type
export interface TitleCandidate {
    title: string;
    formula_tags: string[];
    hook_score: number;
    rationale?: string;
}

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
    lastRequestPayload: { input: string; config: Partial<CreationConfig>; mode?: string } | null;
    // Phase 10: Multi-turn dialogue state
    lastGeneratedContent: string;
    lastSelectedOption: any | null;
    // P10-1: Title AB Testing
    titleCandidates: TitleCandidate[];
    selectedTitle: string;
    // P13: Critic 评分结果
    critiqueResult: {
        score: number;
        verdict: string;
        dimensions: Record<string, { score: number; reason: string }>;
        penalties: Array<{ item: string; deduction: number; detail: string }>;
        suggestions: string[];
    } | null;

    // Actions
    startSession: (payload: { input: string, config: Partial<CreationConfig> }) => Promise<void>;
    confirmStrategy: (option: any, selectedTitle?: string) => Promise<void>; // Step 2 Trigger
    regenerate: () => Promise<void>; // Re-run with same settings
    stopSession: () => void;
    resetSession: () => void;
    setSelectedTitle: (title: string) => void; // P10-1
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
    lastGeneratedContent: '',
    lastSelectedOption: null,
    // P10-1: Title AB Testing
    titleCandidates: [],
    selectedTitle: '',
    // P13: Critic 评分结果
    critiqueResult: null,

    startSession: async ({ input, config }) => {
        // P14-B: Load Agent Models & Provider Keys
        const agentModels = useAgentModelStore.getState().models;
        let providerKeys: Record<string, string> = {};
        try {
            const storedKeys = localStorage.getItem('qs_provider_keys');
            if (storedKeys) providerKeys = JSON.parse(storedKeys);
        } catch (e) {
            console.error("Failed to load provider keys", e);
        }

        const apiConfig = getAPIConfig(); // Legacy global

        // Construct Agent Config Payload
        const agentConfigPayload: Record<string, any> = {};
        const roles = ['strategist', 'writer', 'critic', 'polisher'] as const;

        roles.forEach(role => {
            const modelConfig = agentModels[role];
            if (modelConfig) {
                let apiKey = providerKeys[modelConfig.provider];
                if (!apiKey && apiConfig?.provider === modelConfig.provider) {
                    apiKey = apiConfig.api_key;
                }
                agentConfigPayload[role] = {
                    provider: modelConfig.provider,
                    model_id: modelConfig.model,
                    api_key: apiKey || ''
                };
            }
        });

        // P14: 检查是否为 hot_take 模式 - 使用独立流程
        if (config.mode === 'hot_take') {
            // Hot Take 模式: 直接调用 /hot_take，跳过策略师
            set({
                status: 'connecting',
                error: null,
                content: '',
                steps: [{ id: 'step-hottake', agent: 'writer', label: '锐评生成', status: 'active', message: '正在生成锐评...' }],
                strategyOptions: null,
                analysisResult: null,
                agentLogs: [],
                isWaitingForSelection: false,
                lastRequestPayload: { input, config, mode: 'hot_take' }
            });

            try {
                const endpoint = `${API_BASE_URL}/hot_take`;

                // P14-C: 使用模式专属 Writer 配置
                const modeWriterConfig = useModeWriterStore.getState().getWriterForMode('hot_take');
                const apiKey = providerKeys[modeWriterConfig.provider] || '';

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input: input.trim(),
                        api_config: {
                            provider: modeWriterConfig.provider,
                            model_id: modeWriterConfig.model,
                            api_key: apiKey
                        },
                        agent_config: agentConfigPayload // P14-B
                    }),
                });

                if (!response.ok) throw new Error(`Hot Take 生成失败: ${response.statusText}`);

                const result = await response.json();

                // 解析候选结果
                const candidates = result.result?.candidates || [];

                // P14-Fix: 直接显示所有锐评结果，不需要选择
                const contentLines = candidates.map((c: any, i: number) =>
                    `### 锐评 ${i + 1}\n\n${c.content || c.text || '(无内容)'}\n\n---`
                ).join('\n\n');

                set({
                    status: 'completed',
                    content: contentLines || '未能生成锐评内容',
                    lastGeneratedContent: contentLines,
                    isWaitingForSelection: false,
                    steps: [{ id: 'step-hottake', agent: 'writer', label: '锐评生成', status: 'completed', message: `生成了 ${candidates.length} 条锐评` }]
                });

                toast.success(`锐评生成完成！共 ${candidates.length} 条`);

            } catch (err: unknown) {
                handleError(err, set, get);
            }
            return;
        }

        // 其他模式: 走完整策略师流程
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
            lastRequestPayload: { input, config, mode: config.mode || 'deep_analysis' } as { input: string; config: Partial<CreationConfig>; mode?: string }
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
            // Backend expects: { input, mode, style, length, narrative_type, references, api_config }

            // P14-C: 使用模式专属 Writer 配置覆盖 agent_config.writer
            const currentMode = config.mode || 'deep_analysis';
            const modeWriterConfig = useModeWriterStore.getState().getWriterForMode(currentMode);
            const modeWriterApiKey = providerKeys[modeWriterConfig.provider] || '';

            const finalAgentConfig = {
                ...agentConfigPayload,
                writer: {
                    provider: modeWriterConfig.provider,
                    model_id: modeWriterConfig.model,
                    api_key: modeWriterApiKey
                }
            };

            const requestBody = {
                input: finalInput,
                mode: currentMode,
                style: config.style || 'mimeng',
                length: config.length || 'thread',  // P11: 默认 thread
                retention_level: config.retention_level || 3,  // P13: 添加保留度
                temperature: config.temperature || 0.7,
                narrative_type: 'project_review',
                references: [],
                // P13: 添加 API 配置
                api_config: getAPIConfig(),
                agent_config: finalAgentConfig, // P14-C: 使用覆盖后的配置
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
        // P14: hot_take 模式 - 直接使用选中的候选作为最终内容
        const { lastRequestPayload } = get();
        if (lastRequestPayload?.mode === 'hot_take') {
            // 锐评模式: 选中即完成，不需要再调用 /generate
            set({
                isWaitingForSelection: false,
                status: 'completed',
                content: option.angle || option.content || '',  // 候选内容
                steps: [{ id: 'step-hottake', agent: 'writer', label: '锐评生成', status: 'completed', message: '已选择候选' }],
                lastGeneratedContent: option.angle || option.content || '',
                lastSelectedOption: option
            });
            toast.success('锐评已选择！');
            return;
        }

        // 其他模式: 走完整 /generate 流程
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
            const finalInput = injectPrompts(lastRequestPayload.input || '');

            // Backend expects: { input, mode, style, length, retention_level, narrative_type, references, selected_option, info_anchors }
            // P14-B: Reload agent config for generate phase
            const agentModels = useAgentModelStore.getState().models;
            let providerKeys: Record<string, string> = {};
            try {
                const storedKeys = localStorage.getItem('qs_provider_keys');
                if (storedKeys) providerKeys = JSON.parse(storedKeys);
            } catch (e) {
                console.error("Failed to load provider keys", e);
            }

            const agentConfigPayload: Record<string, any> = {};
            const roles = ['strategist', 'writer', 'critic', 'polisher'] as const;
            roles.forEach(role => {
                const modelConfig = agentModels[role];
                if (modelConfig) {
                    const apiKey = providerKeys[modelConfig.provider] || '';
                    agentConfigPayload[role] = {
                        provider: modelConfig.provider,
                        model_id: modelConfig.model,
                        api_key: apiKey
                    };
                }
            });

            // P14-C: 使用模式专属 Writer 配置覆盖
            const currentMode = lastRequestPayload.config?.mode || lastRequestPayload.mode || 'deep_analysis';
            const modeWriterConfig = useModeWriterStore.getState().getWriterForMode(currentMode);
            const modeWriterApiKey = providerKeys[modeWriterConfig.provider] || '';

            const finalAgentConfig = {
                ...agentConfigPayload,
                writer: {
                    provider: modeWriterConfig.provider,
                    model_id: modeWriterConfig.model,
                    api_key: modeWriterApiKey
                }
            };

            const requestBody = {
                input: finalInput,
                mode: currentMode,
                style: lastRequestPayload.config?.style || 'mimeng',
                length: lastRequestPayload.config?.length || 'thread',  // P11
                retention_level: lastRequestPayload.config?.retention_level || 3,
                narrative_type: 'project_review',
                references: [],
                selected_option: option,
                info_anchors: analysisResult?.info_anchors,
                // P14-C: Include Mode Writer override
                api_config: getAPIConfig(),
                agent_config: finalAgentConfig
            };

            const response = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) throw new Error(`Failed to generate: ${response.statusText}`);
            if (!response.body) throw new Error('No response body received');

            // Save selected option for potential regeneration
            set({ lastSelectedOption: option });

            // Process SSE stream (reuse existing helper)
            await processStream(response.body, set, get);

        } catch (err: unknown) {
            handleError(err, set, get);
        }
    },

    regenerate: async () => {
        // Phase 10: Re-run generation with same settings
        const { lastRequestPayload, lastSelectedOption, analysisResult } = get();

        if (!lastRequestPayload || !lastSelectedOption) {
            toast.error('没有可重新生成的内容，请先完成一次创作');
            return;
        }

        // Reset content but keep state
        set({
            status: 'writing',
            content: '',
            steps: get().steps.map((s, i) => ({
                ...s,
                status: i === 1 ? 'active' : i === 0 ? 'completed' : 'idle',
                message: i === 1 ? '重新撰写中...' : s.message
            }))
        });

        try {
            const finalInput = injectPrompts(lastRequestPayload.input || '');

            // P14-B: Reload agent config for regenerate
            const agentModels = useAgentModelStore.getState().models;
            let providerKeys: Record<string, string> = {};
            try {
                const storedKeys = localStorage.getItem('qs_provider_keys');
                if (storedKeys) providerKeys = JSON.parse(storedKeys);
            } catch (e) {
                console.error("Failed to load provider keys", e);
            }

            const agentConfigPayload: Record<string, any> = {};
            const roles = ['strategist', 'writer', 'critic', 'polisher'] as const;
            roles.forEach(role => {
                const modelConfig = agentModels[role];
                if (modelConfig) {
                    const apiKey = providerKeys[modelConfig.provider] || '';
                    agentConfigPayload[role] = {
                        provider: modelConfig.provider,
                        model_id: modelConfig.model,
                        api_key: apiKey
                    };
                }
            });

            // P14-C: 使用模式专属 Writer 配置覆盖
            const currentMode = lastRequestPayload.mode || lastRequestPayload.config?.mode || 'deep_analysis';
            const modeWriterConfig = useModeWriterStore.getState().getWriterForMode(currentMode);
            const modeWriterApiKey = providerKeys[modeWriterConfig.provider] || '';

            const finalAgentConfig = {
                ...agentConfigPayload,
                writer: {
                    provider: modeWriterConfig.provider,
                    model_id: modeWriterConfig.model,
                    api_key: modeWriterApiKey
                }
            };

            const requestBody = {
                input: finalInput,
                mode: currentMode,
                style: lastRequestPayload.config?.style || 'mimeng',
                length: lastRequestPayload.config?.length || 'thread',
                retention_level: lastRequestPayload.config?.retention_level || 3,
                narrative_type: 'project_review',
                references: [],
                selected_option: lastSelectedOption,
                info_anchors: analysisResult?.info_anchors,
                // P14-C: Include Mode Writer override
                api_config: getAPIConfig(),
                agent_config: finalAgentConfig
            };

            const response = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) throw new Error(`Failed to regenerate: ${response.statusText}`);
            if (!response.body) throw new Error('No response body received');

            await processStream(response.body, set, get);
            toast.success('重新生成完成');

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
            isWaitingForSelection: false,
            lastGeneratedContent: '',
            lastSelectedOption: null,
            // P10-1: Reset title state
            titleCandidates: [],
            selectedTitle: ''
        });
    },

    // P10-1: Set selected title
    setSelectedTitle: (title: string) => {
        set({ selectedTitle: title });
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
                    console.log('[SSE] Event received:', event.type, event);
                    handleEvent(event, set, get);
                } catch (e) { console.warn('SSE Parse Error', e, line); }
            }
        }
    }

    // Process any remaining buffer content
    if (buffer.startsWith('data: ')) {
        try {
            const event = JSON.parse(buffer.slice(6));
            console.log('[SSE] Final buffer event:', event.type, event);
            handleEvent(event, set, get);
        } catch (e) { console.warn('SSE Final Parse Error', e, buffer); }
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
                // Update status and main message
                steps[stepIndex].status = 'thinking';
                steps[stepIndex].message = event.detail;

                // P10-4: Append to subSteps for detailed view
                const newSubStep = {
                    id: `step-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    text: event.detail || '',
                    timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false })
                };

                // Ensure subSteps array exists and append
                const currentSubSteps = steps[stepIndex].subSteps || [];
                steps[stepIndex].subSteps = [...currentSubSteps, newSubStep];

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
            // P10-1: Now also receives title_candidates
            const payload = event.payload; // { info_anchors, options, style_notes, title_candidates }
            if (payload && payload.options) {
                set({
                    strategyOptions: payload.options,
                    analysisResult: {
                        info_anchors: payload.info_anchors,
                        style_notes: payload.style_notes
                    },
                    // P10-1: Title Candidates
                    titleCandidates: payload.title_candidates || [],
                    selectedTitle: payload.title_candidates?.[0]?.title || '',
                    isWaitingForSelection: true,
                    status: 'listening'
                });
                toast.success("策略分析完成，请选择标题和角度");
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
        case 'critique_update': {
            // P13: 处理 Critic 评分详情
            set({
                critiqueResult: {
                    score: event.score,
                    verdict: event.verdict,
                    dimensions: event.dimensions,
                    penalties: event.penalties,
                    suggestions: event.suggestions
                }
            });
            console.log('[P13] Critique update received:', event.score, event.verdict);
            break;
        }
    }
}

// Types needed for compilation (re-declare or import if missing)
interface BackendEvent {
    type: 'thinking_step' | 'agent_update' | 'final_result' | 'error' | 'end' | 'analysis_result' | 'critique_update';
    // P13: critique_update 字段
    score?: number;
    verdict?: string;
    dimensions?: Record<string, { score: number; reason: string }>;
    penalties?: Array<{ item: string; deduction: number; detail: string }>;
    suggestions?: string[];
    agent?: string;
    step?: string;
    status?: string;
    detail?: string;
    payload?: any;
    message?: string;
    logs?: string[];
}
