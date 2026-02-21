'use client';

import { ReactNode, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { StudioNavbar } from "@/features/studio/components/layout/StudioNavbar";
import { useAgentStore, mapStatusToPhase, StudioPhase } from "@/features/agent/stores/useAgentStore";
import { cn } from "@/lib/utils";
import { DataPanel } from "@/features/studio/components/DataPanel";
import { MODES_WITH_DATA_PANEL } from "@/config/constants";
import { CreationModeSchema, type CreationMode } from "@/features/studio/schema";

interface StudioLayoutProps {
    children: ReactNode;
    leftPanel?: ReactNode;
    rightPanel?: ReactNode;
}

/**
 * StudioLayout v5 - P27 DataPanel 分栏
 * 
 * 核心策略:
 * 1. 左右面板使用 fixed 定位，固定在屏幕两侧
 * 2. 中间 main 使用 margin 避让侧边栏 (P27: 动态感知 ConfigIsland 展开/收起)
 * 3. P27: 根据模式渲染 DataPanel，与 WritingCanvas 左右并排
 */
export function StudioLayout({ children, leftPanel, rightPanel }: StudioLayoutProps) {
    const { status } = useAgentStore();
    const phase = mapStatusToPhase(status);
    const hasRightPanel = !!rightPanel;
    const hasLeftPanel = !!leftPanel;

    // P27: 监听 ConfigIsland 展开/收起状态
    const [configExpanded, setConfigExpanded] = useState(true);

    useEffect(() => {
        const checkExpanded = () => {
            const val = document.documentElement.getAttribute('data-config-expanded');
            setConfigExpanded(val !== 'false');
        };
        checkExpanded();
        const observer = new MutationObserver(checkExpanded);
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-config-expanded'] });
        return () => observer.disconnect();
    }, []);

    // P27: 读取当前模式，判断是否需要 DataPanel
    const searchParams = useSearchParams();
    const modeParam = searchParams.get('mode') || 'mid_article';
    const currentMode = CreationModeSchema.safeParse(modeParam).success
        ? (modeParam as CreationMode)
        : 'mid_article';
    const hasDataPanel = hasLeftPanel && MODES_WITH_DATA_PANEL.includes(currentMode);

    return (
        <div className="flex flex-col h-screen overflow-hidden bg-canvas text-ink-primary font-sans relative selection:bg-zinc-900 selection:text-white">

            {/* Layer 0: Background Texture */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none z-0"
                style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '24px 24px' }} />

            {/* Layer 1: Navbar */}
            <div className="z-50 flex-shrink-0 relative">
                <StudioNavbar />
            </div>

            {/* Main Body - Flex Row */}
            <div className="flex flex-1 overflow-hidden relative z-10">

                {/* Left Sidebar - 360px fixed width */}
                {leftPanel && (
                    <aside className="w-[360px] flex-shrink-0 border-r border-zinc-200 bg-white hidden lg:flex flex-col overflow-hidden z-20 shadow-[2px_0_8px_rgba(0,0,0,0.02)]">
                        {leftPanel}
                    </aside>
                )}

                {/* Data Panel - conditionally rendered, 360px fixed width */}
                {hasDataPanel && (
                    <div className="w-[360px] flex-shrink-0 border-r border-zinc-200 bg-[#fafafa] hidden xl:flex flex-col overflow-hidden z-10 shadow-[2px_0_8px_rgba(0,0,0,0.02)]">
                        <DataPanel mode={currentMode} />
                    </div>
                )}

                {/* Main Workspace - Flexible central area */}
                <main className="flex-1 flex flex-col relative bg-[#f4f4f5] overflow-hidden min-w-0 z-0">
                    {children}
                </main>

                {/* Right Sidebar - 360px fixed width */}
                {hasRightPanel && (
                    <aside className="w-[360px] flex-shrink-0 border-l border-zinc-200 bg-[#fafafa] hidden 2xl:flex flex-col overflow-hidden z-20 shadow-[-2px_0_8px_rgba(0,0,0,0.02)]">
                        {rightPanel}
                    </aside>
                )}
            </div>

        </div>
    );
}
