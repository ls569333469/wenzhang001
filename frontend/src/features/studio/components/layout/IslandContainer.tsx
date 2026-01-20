import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface IslandContainerProps {
    children: ReactNode;
    position?: 'left' | 'right' | 'center';
    className?: string;
}

/**
 * IslandContainer - 通用岛屿容器
 * 
 * 核心样式:
 * - fixed: 固定定位
 * - bg-white: 白色背景
 * - rounded-2xl: 20px 圆角
 * - shadow-island: 专属岛屿阴影
 * - border-zinc-100: 极细边框
 * - z-40: 这里的 z-index 低于 Navbar (z-50) 但高于 Canvas
 */
export function IslandContainer({ children, position, className }: IslandContainerProps) {
    return (
        <aside className={cn(
            "fixed bg-white rounded-2xl shadow-island border border-zinc-100 z-40 flex flex-col overflow-hidden transition-all duration-300",
            // Position Presets
            position === 'left' && "left-6 top-24 bottom-6 w-80",
            position === 'right' && "right-6 top-24 bottom-6 w-72",
            position === 'center' && "left-1/2 -translate-x-1/2 top-24 bottom-6 max-w-4xl w-full",
            className
        )}>
            {children}
        </aside>
    );
}
