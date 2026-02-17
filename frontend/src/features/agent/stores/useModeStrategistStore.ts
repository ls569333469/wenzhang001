/**
 * P24-D: 模式专属 Strategist 配置 Store
 * 
 * 每个创作模式可配置独立的 Strategist 模型
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
    ModeStrategistConfig,
    DEFAULT_MODE_STRATEGISTS,
    AgentModelSetting
} from '../../studio/schema';

interface ModeStrategistStore {
    /** 所有模式的 Strategist 配置 */
    strategists: ModeStrategistConfig;

    /** 更新指定模式的 Strategist 配置 */
    updateStrategist: (mode: keyof ModeStrategistConfig, setting: Partial<AgentModelSetting>) => void;

    /** 获取指定模式的 Strategist 配置 */
    getStrategistForMode: (mode: string) => AgentModelSetting;

    /** 重置为默认配置 */
    reset: () => void;
}

export const useModeStrategistStore = create<ModeStrategistStore>()(
    persist(
        (set, get) => ({
            strategists: DEFAULT_MODE_STRATEGISTS,

            updateStrategist: (mode, setting) =>
                set((state) => ({
                    strategists: {
                        ...state.strategists,
                        [mode]: { ...state.strategists[mode], ...setting }
                    }
                })),

            getStrategistForMode: (mode: string) => {
                const state = get();

                if (mode in state.strategists) {
                    return state.strategists[mode as keyof ModeStrategistConfig];
                }

                // 默认返回 mid_article 配置
                return state.strategists.mid_article;
            },

            reset: () => set({ strategists: DEFAULT_MODE_STRATEGISTS })
        }),
        {
            name: 'qs_mode_strategists',
            version: 1,
            skipHydration: true,
        }
    )
);
