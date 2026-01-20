'use client';

import { create } from 'zustand';

/**
 * useStudioUI - UI State Store
 * 
 * 仅用于管理非业务的 UI 状态，例如：
 * - 侧边栏折叠/展开
 * - 弹窗开关
 * - 视图模式切换
 */

interface StudioUIState {
    // Canvas State
    viewMode: 'split' | 'full';
    toggleViewMode: () => void;

    // Sidebar State
    isConfigOpen: boolean;
    toggleConfig: () => void;

    // Actions
    reset: () => void;
}

export const useStudioUI = create<StudioUIState>((set) => ({
    viewMode: 'split',
    toggleViewMode: () => set((state) => ({
        viewMode: state.viewMode === 'split' ? 'full' : 'split'
    })),

    isConfigOpen: true,
    toggleConfig: () => set((state) => ({
        isConfigOpen: !state.isConfigOpen
    })),

    reset: () => set({ viewMode: 'split', isConfigOpen: true }),
}));
