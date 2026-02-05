/**
 * P14-C: 模式专属 Writer 配置 Store
 * 
 * 每个创作模式可配置独立的 Writer 模型
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
    ModeWriterConfig,
    DEFAULT_MODE_WRITERS,
    AgentModelSetting
} from '../../studio/schema';

interface ModeWriterStore {
    /** 所有模式的 Writer 配置 */
    writers: ModeWriterConfig;

    /** 更新指定模式的 Writer 配置 */
    updateWriter: (mode: keyof ModeWriterConfig, setting: Partial<AgentModelSetting>) => void;

    /** 获取指定模式的 Writer 配置 (P18: 直接获取, 无别名) */
    getWriterForMode: (mode: string) => AgentModelSetting;

    /** 重置为默认配置 */
    reset: () => void;
}

export const useModeWriterStore = create<ModeWriterStore>()(
    persist(
        (set, get) => ({
            writers: DEFAULT_MODE_WRITERS,

            updateWriter: (mode, setting) =>
                set((state) => ({
                    writers: {
                        ...state.writers,
                        [mode]: { ...state.writers[mode], ...setting }
                    }
                })),

            getWriterForMode: (mode: string) => {
                const state = get();

                // P18: 直接使用 mode (Clean Break)
                // 如果模式存在于配置中，返回配置
                if (mode in state.writers) {
                    return state.writers[mode as keyof ModeWriterConfig];
                }

                // 默认返回 hot_take 配置 (最安全)
                return state.writers.hot_take;
            },

            reset: () => set({ writers: DEFAULT_MODE_WRITERS })
        }),
        {
            name: 'qs_mode_writers',
            version: 1,
            skipHydration: true, // P14-C: SSR-safe - defer localStorage access to client
        }
    )
);
