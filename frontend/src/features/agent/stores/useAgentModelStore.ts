import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AgentModels, DEFAULT_AGENT_MODELS, AgentModelSetting, PROVIDER_IDS } from '../../studio/schema';

// P14-B: 独立 Store 管理智能体模型配置
interface AgentModelStore {
    models: AgentModels;
    updateModel: (role: keyof AgentModels, setting: Partial<AgentModelSetting>) => void;
    reset: () => void;
}

// P14-B: 有效的 Provider 列表 (用于迁移校验)
const VALID_PROVIDERS = Object.values(PROVIDER_IDS);

export const useAgentModelStore = create<AgentModelStore>()(
    persist(
        (set) => ({
            models: DEFAULT_AGENT_MODELS,

            updateModel: (role, setting) =>
                set((state) => ({
                    models: {
                        ...state.models,
                        [role]: { ...state.models[role], ...setting }
                    }
                })),

            reset: () => set({ models: DEFAULT_AGENT_MODELS })
        }),
        {
            name: 'qs_agent_models', // localStorage key
            version: 2, // P14-B: Bump version to trigger migration (was 1)
            skipHydration: true, // P14-B: SSR-safe - defer localStorage access to client
            migrate: (persistedState: any, version) => {
                // Version 1 -> 2: Remove deprecated providers (deepseek, openai)
                if (version < 2 && persistedState?.models) {
                    const migratedModels: any = { ...DEFAULT_AGENT_MODELS };
                    const roles = ['strategist', 'writer', 'critic', 'polisher'] as const;

                    roles.forEach(role => {
                        const oldSetting = persistedState.models[role];
                        if (oldSetting && VALID_PROVIDERS.includes(oldSetting.provider)) {
                            // Valid provider, keep it but ensure model exists
                            migratedModels[role] = oldSetting;
                        }
                        // Otherwise, use default (volcengine)
                    });

                    console.log('[AgentModelStore] Migrated from v1 to v2:', migratedModels);
                    return { models: migratedModels };
                }
                return persistedState;
            },
        }
    )
);

