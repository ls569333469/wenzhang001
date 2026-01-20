'use client';

import { cn } from "@/lib/utils";

/**
 * RightSidebar Island - Fixed Right Agent Timeline
 * 
 * Style: Floating island with shadow
 * Position: Fixed right
 * 
 * This is a skeleton component - will be replaced with AgentTimeline
 */

interface RightSidebarProps {
    children?: React.ReactNode;
    className?: string;
}

export function RightSidebar({ children, className }: RightSidebarProps) {
    return (
        <aside className={cn(
            // Position
            "fixed right-4 top-20 bottom-4",
            "w-72",
            // Island Style
            "bg-island rounded-2xl shadow-island border border-zinc-100",
            // Layout
            "flex flex-col overflow-hidden",
            className
        )}>
            {children || (
                <div className="flex-1 flex items-center justify-center text-ink-muted">
                    <span className="text-sm">智能体状态占位</span>
                </div>
            )}
        </aside>
    );
}
