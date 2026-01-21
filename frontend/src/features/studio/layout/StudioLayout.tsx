'use client';

import { ReactNode } from "react";
import { StudioNavbar } from "@/features/studio/components/layout/StudioNavbar";
import { useAgentStore, mapStatusToPhase, StudioPhase } from "@/features/agent/stores/useAgentStore";
import { cn } from "@/lib/utils";

interface StudioLayoutProps {
    children: ReactNode;
    leftPanel?: ReactNode;
    rightPanel?: ReactNode;
}

/**
 * StudioLayout v4 - 响应式 Flexbox + Margin 方案
 * 
 * 核心策略:
 * 1. 左右面板使用 fixed 定位，固定在屏幕两侧
 * 2. 中间 main 使用 margin 避让侧边栏
 * 3. 响应式断点自动调整
 */
export function StudioLayout({ children, leftPanel, rightPanel }: StudioLayoutProps) {
    const { status } = useAgentStore();
    const phase = mapStatusToPhase(status);
    const hasRightPanel = phase !== 'idle' && rightPanel;

    return (
        <div className="min-h-screen bg-canvas text-ink-primary font-sans relative selection:bg-zinc-900 selection:text-white">

            {/* Layer 0: Background Texture */}
            <div className="fixed inset-0 opacity-[0.03] pointer-events-none z-0"
                style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '24px 24px' }} />

            {/* Layer 1: Navbar */}
            <StudioNavbar />

            {/* Left Sidebar - Fixed Position */}
            {leftPanel && (
                <aside className={cn(
                    "fixed top-16 left-0 h-[calc(100vh-64px)] z-30",
                    // 响应式: lg以下隐藏，lg以上显示
                    "hidden lg:block"
                )}>
                    {leftPanel}
                </aside>
            )}

            {/* Right Sidebar - Fixed Position (仅活跃状态) */}
            {hasRightPanel && (
                <aside className={cn(
                    "fixed top-16 right-0 h-[calc(100vh-64px)] z-30",
                    "w-[280px]",
                    // 响应式: xl以下隐藏
                    "hidden xl:block"
                )}>
                    {rightPanel}
                </aside>
            )}

            {/* Main Content - 使用 margin 避让侧边栏 */}
            <main className={cn(
                "min-h-screen pt-16",
                // lg 以下: 全宽
                "ml-0 mr-0",
                // lg 以上: 避让左侧栏 (320px)
                "lg:ml-[320px]",
                // xl 以上 + 活跃状态: 同时避让右侧栏 (280px)
                hasRightPanel && "xl:mr-[280px]",
                // 居中和填充
                "flex flex-col items-center justify-start",
                "p-6 pt-24"
            )}>
                {/* 内容容器 - 流体宽度 */}
                <div className={cn(
                    "w-full max-w-2xl px-4",
                    // 活跃状态时扩展宽度
                    phase !== 'idle' && "max-w-4xl"
                )}>
                    {children}
                </div>
            </main>

            {/* 移动端菜单按钮 (lg 以下可见) */}
            <div className="fixed bottom-4 left-4 z-50 lg:hidden">
                <button className="w-12 h-12 bg-zinc-900 text-white rounded-full shadow-lg flex items-center justify-center">
                    ⚙️
                </button>
            </div>
        </div>
    );
}
