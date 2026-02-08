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

export interface WriterPrompts {
    hot_take: PromptSection;
    short_article: PromptSection;
    mid_article: PromptSection;
    long_article: PromptSection;
    tutorial: PromptSection;
    rewrite: PromptSection;
}

export interface CustomPromptsState {
    customPrompts: {
        enabled: boolean;
        writer: WriterPrompts;
        strategist: PromptSection;
        critic: PromptSection;
        polisher: PromptSection;
    };

    // Actions
    toggleEnabled: (enabled: boolean) => void;
    updateWriterPrompt: (mode: keyof WriterPrompts, section: Partial<PromptSection>) => void;
    updateStrategistPrompt: (section: Partial<PromptSection>) => void;
    updateCriticPrompt: (section: Partial<PromptSection>) => void;
    updatePolisherPrompt: (section: Partial<PromptSection>) => void;
    resetToDefaults: () => void;

    // Selectors/Helpers
    getAssembledPrompt: (agent: 'writer' | 'strategist' | 'critic' | 'polisher', mode?: keyof WriterPrompts, input?: string) => string;
}

export const usePromptStore = create<CustomPromptsState>()(
    persist(
        (set, get) => ({
            customPrompts: {
                enabled: false,
                writer: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.writer)), // Deep copy defaults
                strategist: { ...DEFAULT_PROMPTS.strategist },
                critic: { ...DEFAULT_PROMPTS.critic },
                polisher: { ...DEFAULT_PROMPTS.polisher }
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

            updateStrategistPrompt: (section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    strategist: { ...state.customPrompts.strategist, ...section }
                }
            })),

            updateCriticPrompt: (section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    critic: { ...state.customPrompts.critic, ...section }
                }
            })),

            updatePolisherPrompt: (section) => set((state) => ({
                customPrompts: {
                    ...state.customPrompts,
                    polisher: { ...state.customPrompts.polisher, ...section }
                }
            })),

            resetToDefaults: () => set({
                customPrompts: {
                    enabled: false,
                    writer: JSON.parse(JSON.stringify(DEFAULT_PROMPTS.writer)),
                    strategist: { ...DEFAULT_PROMPTS.strategist },
                    critic: { ...DEFAULT_PROMPTS.critic },
                    polisher: { ...DEFAULT_PROMPTS.polisher }
                }
            }),

            getAssembledPrompt: (agent, mode, input = '{{ raw_input }}') => {
                const state = get();
                let section: PromptSection; // = { role: '', task: '', style: '', forbidden: '' };
                let outputSchema = '';

                if (agent === 'writer' && mode) {
                    section = state.customPrompts.writer[mode];
                    outputSchema = OUTPUT_FORMATS[mode] || '';
                } else if (agent === 'strategist') {
                    section = state.customPrompts.strategist;
                } else if (agent === 'critic') {
                    section = state.customPrompts.critic;
                } else {
                    section = state.customPrompts.polisher;
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
            version: 3, // P22: Bump version for short_article
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
                        // Rename quick_summary → mid_article (中篇)
                        if (persistedState.customPrompts.writer.quick_summary) {
                            persistedState.customPrompts.writer.mid_article = persistedState.customPrompts.writer.quick_summary;
                            delete persistedState.customPrompts.writer.quick_summary;
                        }
                        // Rename deep_analysis → long_article (长篇)
                        if (persistedState.customPrompts.writer.deep_analysis) {
                            persistedState.customPrompts.writer.long_article = persistedState.customPrompts.writer.deep_analysis;
                            delete persistedState.customPrompts.writer.deep_analysis;
                        }
                    }
                    // Ensure new keys exist with defaults if missing
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
                return persistedState as CustomPromptsState;
            }
        }
    )
);
