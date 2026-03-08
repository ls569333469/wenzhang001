/**
 * P24-D: 模式专属 Critic 配置 Store
 * 
 * 每个创作模式可配置独立的 Critic 模型
 * v2: 扩展到 6 模式（加入 hot_take）
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
    ModeCriticConfig,
    DEFAULT_MODE_CRITICS,
    AgentModelSetting
} from '../../studio/schema';

interface ModeCriticStore {
    /** 所有模式的 Critic 配置 */
    critics: ModeCriticConfig;

    /** 更新指定模式的 Critic 配置 */
    updateCritic: (mode: keyof ModeCriticConfig, setting: Partial<AgentModelSetting>) => void;

    /** 获取指定模式的 Critic 配置 */
    getCriticForMode: (mode: string) => AgentModelSetting;

    /** 重置为默认配置 */
    reset: () => void;
}

export const useModeCriticStore = create<ModeCriticStore>()(
    persist(
        (set, get) => ({
            critics: DEFAULT_MODE_CRITICS,

            updateCritic: (mode, setting) =>
                set((state) => ({
                    critics: {
                        ...state.critics,
                        [mode]: { ...state.critics[mode], ...setting }
                    }
                })),

            getCriticForMode: (mode: string) => {
                const state = get();

                if (mode in state.critics) {
                    return state.critics[mode as keyof ModeCriticConfig];
                }

                // 默认返回 mid_article 配置
                return state.critics.mid_article;
            },

            reset: () => set({ critics: DEFAULT_MODE_CRITICS })
        }),
        {
            name: 'qs_mode_critics',
            version: 3,  // P34: v2→v3 (8→9 modes, +binance_square)
            skipHydration: true,
            migrate: (persistedState: any, version: number) => {
                const old = persistedState as any;
                if (version < 2) {
                    // v1→v2: 添加 hot_take key
                    if (old.critics && !old.critics.hot_take) {
                        old.critics.hot_take = { provider: 'volcengine', model: '' };
                    }
                }
                if (version < 3) {
                    // v2→v3: 添加 binance_square key
                    if (old.critics && !old.critics.binance_square) {
                        old.critics.binance_square = { provider: 'volcengine', model: 'doubao-seed-2-0-lite-260215' };
                    }
                }
                return persistedState as ModeCriticStore;
            },
        }
    )
);
