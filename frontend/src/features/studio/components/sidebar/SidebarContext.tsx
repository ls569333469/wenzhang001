'use client';

import { createContext, useContext } from 'react';

export type SidebarTabId = 'progress' | 'thinking' | 'version' | 'logs' | 'export';

interface SidebarContextType {
    activeTab: SidebarTabId;
    setActiveTab: (tab: SidebarTabId) => void;
}

export const SidebarContext = createContext<SidebarContextType | null>(null);

export function useSidebar() {
    const context = useContext(SidebarContext);
    if (!context) {
        throw new Error('useSidebar must be used within a SidebarProvider (UnifiedSidebar)');
    }
    return context;
}
