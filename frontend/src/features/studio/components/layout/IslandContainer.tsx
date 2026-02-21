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
 * 左侧: 独立 fixed 定位 + 岛屿阴影
 * 右侧: 简洁左边框分隔 (无圆角，填充父容器)
 */
export function IslandContainer({ children, position, className }: IslandContainerProps) {
    return (
        <aside className={cn(
            "flex flex-col overflow-hidden transition-all duration-300",
            // 共用样式根据 position 不同
            position === 'left' && "fixed left-6 top-24 bottom-6 z-40 bg-white rounded-2xl shadow-island border border-zinc-100",
            position === 'right' && "h-full w-full bg-white border-l border-zinc-200", // 简洁边框
            position === 'center' && "fixed left-1/2 -translate-x-1/2 top-24 bottom-6 max-w-4xl w-full z-40 bg-white rounded-2xl shadow-island border border-zinc-100",
            className
        )}>
            {children}
        </aside>
    );
}
