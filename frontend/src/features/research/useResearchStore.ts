'use client';

import { create } from 'zustand';

/**
 * P31 P0: 投研模块共享状态
 * 
 * ResearchPanel (左侧) 生成日报后 → 触发 triggerRefresh
 * ResearchView (主区域) 监听 refreshKey 变化 → 自动 refetch /latest
 */

interface ResearchState {
    /** 递增 key，变化时触发 ResearchView refetch */
    refreshKey: number;
    /** 是否正在生成日报 */
    isGenerating: boolean;
    /** 生成状态消息 */
    statusMessage: string;
    /** 生成完成后触发刷新 */
    triggerRefresh: () => void;
    /** 设置生成状态 */
    setGenerating: (generating: boolean, message?: string) => void;
}

export const useResearchStore = create<ResearchState>((set) => ({
    refreshKey: 0,
    isGenerating: false,
    statusMessage: '',
    triggerRefresh: () => set((state) => ({ refreshKey: state.refreshKey + 1 })),
    setGenerating: (generating, message = '') => set({ isGenerating: generating, statusMessage: message }),
}));
