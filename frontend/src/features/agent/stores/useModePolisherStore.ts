/**
 * P24-D: 模式专属 Polisher 配置 Store
 * 
 * 每个创作模式可配置独立的 Polisher 模型
 * v2: 扩展到 6 模式（加入 hot_take + short_article）
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
    ModePolisherConfig,
    DEFAULT_MODE_POLISHERS,
    AgentModelSetting
} from '../../studio/schema';

interface ModePolisherStore {
    /** 所有模式的 Polisher 配置 */
    polishers: ModePolisherConfig;

    /** 更新指定模式的 Polisher 配置 */
    updatePolisher: (mode: keyof ModePolisherConfig, setting: Partial<AgentModelSetting>) => void;

    /** 获取指定模式的 Polisher 配置 */
    getPolisherForMode: (mode: string) => AgentModelSetting;

    /** 重置为默认配置 */
    reset: () => void;
}

export const useModePolisherStore = create<ModePolisherStore>()(
    persist(
        (set, get) => ({
            polishers: DEFAULT_MODE_POLISHERS,

            updatePolisher: (mode, setting) =>
                set((state) => ({
                    polishers: {
                        ...state.polishers,
                        [mode]: { ...state.polishers[mode], ...setting }
                    }
                })),

            getPolisherForMode: (mode: string) => {
                const state = get();

                if (mode in state.polishers) {
                    return state.polishers[mode as keyof ModePolisherConfig];
                }

                // 默认返回 mid_article 配置
                return state.polishers.mid_article;
            },

            reset: () => set({ polishers: DEFAULT_MODE_POLISHERS })
        }),
        {
            name: 'qs_mode_polishers',
            version: 3,  // P34: v2→v3 (8→9 modes, +binance_square)
            skipHydration: true,
            migrate: (persistedState: any, version: number) => {
                const old = persistedState as any;
                if (version < 2) {
                    // v1→v2: 添加 hot_take + short_article keys
                    if (old.polishers) {
                        if (!old.polishers.hot_take) {
                            old.polishers.hot_take = { provider: 'volcengine', model: '' };
                        }
                        if (!old.polishers.short_article) {
                            old.polishers.short_article = { provider: 'volcengine', model: '' };
                        }
                    }
                }
                if (version < 3) {
                    // v2→v3: 添加 binance_square key
                    if (old.polishers && !old.polishers.binance_square) {
                        old.polishers.binance_square = { provider: 'volcengine', model: '' };
                    }
                }
                return persistedState as ModePolisherStore;
            },
        }
    )
);
