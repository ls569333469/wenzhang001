import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { DEFAULT_PROMPTS } from '../constants/defaultPrompts';
import { OUTPUT_FORMATS } from '../constants/promptSchemas';

export interface PromptSection {
    role: string;
    task: string;
    style: string;
    forbidden: string;
}

// P24-D: 统一 per-mode 提示词类型（Writer / Strategist / Critic / Polisher 共用）
export interface WriterPrompts {
    hot_take: PromptSection;
    short_article: PromptSection;
    mid_article: PromptSection;
    long_article: PromptSection;
    tutorial: PromptSection;
    bullish_take: PromptSection;
    kaito_yap: PromptSection;
    project_research: PromptSection;
}

export interface CustomPromptsState {
    customPrompts: {
        enabled: boolean;
        writer: WriterPrompts;
        strategist: WriterPrompts;   // P24-D: changed from PromptSection to WriterPrompts
        critic: WriterPrompts;       // P24-D: changed from PromptSection to WriterPrompts
        polisher: WriterPrompts;     // P24-D: changed from PromptSection to WriterPrompts
    };

    // Actions
    toggleEnabled: (enabled: boolean) => void;
    updateWriterPrompt: (mode: keyof WriterPrompts, section: Partial<PromptSection>) => void;
    updateStrategistPrompt: (mode: keyof WriterPrompts, section: Partial<PromptSection>) => void;  // P24-D: added mode
    updateCriticPrompt: (mode: keyof WriterPrompts, section: Partial<PromptSection>) => void;      // P24-D: added mode
    updatePolisherPrompt: (mode: keyof WriterPrompts, section: Partial<PromptSection>) => void;     // P24-D: added mode
    resetToDefaults: () => void;

    // Selectors/Helpers
    getAssembledPrompt: (agent: 'writer' | 'strategist' | 'critic' | 'polisher', mode?: keyof WriterPrompts, input?: string) => string;
}

export const usePromptStore = create<CustomPromptsState>()(
    persist(
        (set, get) => ({
            customPrompts: {
                enabled: false,
                writer: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.writer)),
                strategist: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.strategist)),   // P24-D: per-mode
                critic: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.critic)),           // P24-D: per-mode
                polisher: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.polisher))        // P24-D: per-mode
            },

            toggleEnabled: (enabled) => set((state) => ({
                customPrompts: { ...state.customPrompts, enabled }
            })),

            updateWriterPrompt: (mode, section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    writer: {
                        ...state.customPrompts.writer,
                        [mode]: { ...state.customPrompts.writer[mode], ...section }
                    }
                }
            })),

            // P24-D: per-mode update for strategist
            updateStrategistPrompt: (mode, section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    strategist: {
                        ...state.customPrompts.strategist,
                        [mode]: { ...state.customPrompts.strategist[mode], ...section }
                    }
                }
            })),

            // P24-D: per-mode update for critic
            updateCriticPrompt: (mode, section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    critic: {
                        ...state.customPrompts.critic,
                        [mode]: { ...state.customPrompts.critic[mode], ...section }
                    }
                }
            })),

            // P24-D: per-mode update for polisher
            updatePolisherPrompt: (mode, section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    polisher: {
                        ...state.customPrompts.polisher,
                        [mode]: { ...state.customPrompts.polisher[mode], ...section }
                    }
                }
            })),

            resetToDefaults: () => set({
                customPrompts: {
                    enabled: false,
                    writer: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.writer)),
                    strategist: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.strategist)),
                    critic: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.critic)),
                    polisher: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.polisher))
                }
            }),

            // P24-D: 统一 getAssembledPrompt — 所有 agent 都支持 per-mode
            getAssembledPrompt: (agent, mode, input = '{{ raw_input }}') => {
                const state = get();
                const effectiveMode = mode || 'mid_article';
                let section: PromptSection;
                let outputSchema = '';

                // P24-D: 所有 agent 统一走 per-mode 路径
                const agentPrompts = state.customPrompts[agent] as WriterPrompts;
                section = agentPrompts[effectiveMode];

                if (agent === 'writer') {
                    outputSchema = OUTPUT_FORMATS[effectiveMode] || '';
                }

                if (!section) return '';

                let prompt = `Current Time: ${new Date().toISOString()}\n\n`;
                prompt += `${section.role}\n\n---\n\n`;
                prompt += `## 任务\n${section.task}\n\n---\n\n`;

                if (section.style?.trim()) {
                    prompt += `## 风格要求\n${section.style}\n\n---\n\n`;
                }

                if (section.forbidden?.trim()) {
                    prompt += `## 严禁\n${section.forbidden}\n\n---\n\n`;
                }

                // System Block (Fixed)
                prompt += `## 素材\n${input}\n\n---\n\n`;

                if (outputSchema) {
                    prompt += outputSchema;
                }

                return prompt;
            }
        }),
        {
            name: 'qs_custom_prompts',
            partialize: (state) => ({ customPrompts: state.customPrompts }),
            version: 8, // P30: Bump v7→v8 for bullish_take B-plan defaults (all 4 agents)
            migrate: (persistedState: any, version: number) => {
                // Version 0→1: mid_take → quick_summary
                if (version === 0) {
                    if (persistedState.customPrompts?.writer?.mid_take) {
                        persistedState.customPrompts.writer.quick_summary = persistedState.customPrompts.writer.mid_take;
                        delete persistedState.customPrompts.writer.mid_take;
                    }
                }
                // Version 1→2: P16 renaming (quick_summary→mid_article, deep_analysis→long_article)
                if (version < 2) {
                    if (persistedState.customPrompts?.writer) {
                        if (persistedState.customPrompts.writer.quick_summary) {
                            persistedState.customPrompts.writer.mid_article = persistedState.customPrompts.writer.quick_summary;
                            delete persistedState.customPrompts.writer.quick_summary;
                        }
                        if (persistedState.customPrompts.writer.deep_analysis) {
                            persistedState.customPrompts.writer.long_article = persistedState.customPrompts.writer.deep_analysis;
                            delete persistedState.customPrompts.writer.deep_analysis;
                        }
                    }
                    if (!persistedState.customPrompts?.writer?.mid_article) {
                        if (!persistedState.customPrompts) persistedState.customPrompts = {};
                        if (!persistedState.customPrompts.writer) persistedState.customPrompts.writer = {};
                        persistedState.customPrompts.writer.mid_article = DEFAULT_PROMPTS.writer.mid_article;
                    }
                    if (!persistedState.customPrompts?.writer?.long_article) {
                        if (!persistedState.customPrompts) persistedState.customPrompts = {};
                        if (!persistedState.customPrompts.writer) persistedState.customPrompts.writer = {};
                        persistedState.customPrompts.writer.long_article = DEFAULT_PROMPTS.writer.long_article;
                    }
                }
                // Version 2→3: P22 add short_article
                if (version < 3) {
                    if (!persistedState.customPrompts?.writer?.short_article) {
                        if (!persistedState.customPrompts) persistedState.customPrompts = {};
                        if (!persistedState.customPrompts.writer) persistedState.customPrompts.writer = {};
                        persistedState.customPrompts.writer.short_article = DEFAULT_PROMPTS.writer.short_article;
                    }
                }
                // Version 3→4: P24-D convert strategist/critic/polisher from flat PromptSection to per-mode
                if (version < 4) {
                    const cp = persistedState.customPrompts;
                    if (cp) {
                        const modes = ['hot_take', 'short_article', 'mid_article', 'long_article', 'tutorial'] as const;
                        for (const agent of ['strategist', 'critic', 'polisher'] as const) {
                            const current = cp[agent];
                            if (current && typeof current.role === 'string') {
                                const expanded: any = {};
                                for (const m of modes) {
                                    expanded[m] = { ...current };
                                }
                                cp[agent] = expanded;
                            } else if (!current) {
                                cp[agent] = JSON.parse(JSON.stringify(DEFAULT_PROMPTS[agent]));
                            }
                        }
                    }
                }
                // Version 4→5: P26 prompt sync — reset short_article for all agents
                if (version < 5) {
                    const cp = persistedState.customPrompts;
                    if (cp) {
                        for (const agent of ['writer', 'strategist', 'critic', 'polisher'] as const) {
                            if (cp[agent] && DEFAULT_PROMPTS[agent]?.short_article) {
                                cp[agent].short_article = { ...DEFAULT_PROMPTS[agent].short_article };
                            }
                        }
                    }
                }
                // Version 5→6: P27 add bullish_take, kaito_yap, project_research defaults for all agents
                if (version < 6) {
                    const cp = persistedState.customPrompts;
                    if (cp) {
                        for (const agent of ['writer', 'strategist', 'critic', 'polisher'] as const) {
                            if (cp[agent]) {
                                if (!cp[agent].bullish_take && DEFAULT_PROMPTS[agent]?.bullish_take) {
                                    cp[agent].bullish_take = { ...DEFAULT_PROMPTS[agent].bullish_take };
                                }
                                if (!cp[agent].kaito_yap && DEFAULT_PROMPTS[agent]?.kaito_yap) {
                                    cp[agent].kaito_yap = { ...DEFAULT_PROMPTS[agent].kaito_yap };
                                }
                                if (!cp[agent].project_research && DEFAULT_PROMPTS[agent]?.project_research) {
                                    cp[agent].project_research = { ...DEFAULT_PROMPTS[agent].project_research };
                                }
                            }
                        }
                    }
                }
                // Version 6→8: P30 reset bullish_take for ALL agents (B-plan defaults)
                if (version < 8) {
                    const cp = persistedState.customPrompts;
                    if (cp) {
                        for (const agent of ['writer', 'strategist', 'critic', 'polisher'] as const) {
                            if (cp[agent] && DEFAULT_PROMPTS[agent]?.bullish_take) {
                                cp[agent].bullish_take = { ...DEFAULT_PROMPTS[agent].bullish_take };
                            }
                        }
                    }
                }
                return persistedState as CustomPromptsState;
            }
        }
    )
);
