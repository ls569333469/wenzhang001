'use client';

import { cn } from "@/lib/utils";

/**
 * LeftSidebar Island - Fixed Left Configuration Panel
 * 
 * Style: Floating island with shadow
 * Position: Fixed left
 * 
 * This is a skeleton component - will be replaced with ConfigPanel
 */

interface LeftSidebarProps {
    children?: React.ReactNode;
    className?: string;
}

export function LeftSidebar({ children, className }: LeftSidebarProps) {
    return (
        <aside className={cn(
            // Position
            "fixed left-4 top-20 bottom-4",
            "w-80",
            // Island Style
            "bg-island rounded-2xl shadow-island border border-zinc-100",
            // Layout
            "flex flex-col overflow-hidden",
            className
        )}>
            {children || (
                <div className="flex-1 flex items-center justify-center text-ink-muted">
                    <span className="text-sm">配置面板占位</span>
                </div>
            )}
        </aside>
    );
}
