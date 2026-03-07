'use client';

import React, { useState, useEffect } from "react";
import { LayoutGrid, Settings, PenTool, FolderOpen, PanelLeftClose, PanelLeft, Search } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const SIDEBAR_COLLAPSED_KEY = 'qs_sidebar_collapsed';

export function AdaptiveSidebar() {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [mounted, setMounted] = useState(false);

    // Load collapsed state from localStorage
    useEffect(() => {
        const stored = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
        if (stored === 'true') setIsCollapsed(true);
        setMounted(true);
    }, []);

    // Save collapsed state to localStorage
    const toggleCollapsed = () => {
        const newValue = !isCollapsed;
        setIsCollapsed(newValue);
        localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(newValue));
    };

    const navItems = [
        { href: "/dashboard", icon: LayoutGrid, label: "仪表盘" },
        { href: "/studio", icon: PenTool, label: "创作中心" },
        { href: "/data", icon: FolderOpen, label: "数据中心" },
        { href: "/settings", icon: Settings, label: "系统设置" },
    ];

    // Prevent hydration mismatch
    if (!mounted) {
        return <aside className="w-[280px] h-full bg-paper border-r border-hairline" />;
    }

    return (
        <aside
            className={cn(
                "h-full flex flex-col border-r border-hairline bg-paper text-ink-primary overflow-hidden transition-all duration-300",
                isCollapsed ? "w-16" : "w-[280px]"
            )}
        >
            {/* 顶部固定区 */}
            <div className="h-14 flex items-center justify-between px-3 border-b border-hairline shrink-0">
                {!isCollapsed && (
                    <Link href="/dashboard" className="flex-1 min-w-0 hover:opacity-80 transition-opacity">
                        <h1 className="text-base font-serif font-medium text-ink-primary truncate">量子工坊</h1>
                        <p className="text-[10px] text-ink-muted uppercase tracking-wider">v6.2</p>
                    </Link>
                )}
                <button
                    onClick={toggleCollapsed}
                    className={cn(
                        "p-2 rounded-sm hover:bg-zinc-200/50 transition-colors text-ink-muted hover:text-ink-primary",
                        isCollapsed && "mx-auto"
                    )}
                    title={isCollapsed ? "展开侧边栏" : "收起侧边栏"}
                >
                    {isCollapsed ? <PanelLeft size={18} /> : <PanelLeftClose size={18} />}
                </button>
            </div>

            {/* 滚动内容区 */}
            <div className="flex-1 overflow-y-auto p-2 space-y-4">
                {/* 导航菜单 */}
                <div className="space-y-1">
                    {!isCollapsed && (
                        <div className="px-2 text-[10px] font-semibold text-ink-muted uppercase tracking-wider mb-2">
                            导航
                        </div>
                    )}
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "w-full flex items-center gap-3 px-3 py-2.5 text-sm rounded-sm transition-colors text-left group relative",
                                pathname === item.href
                                    ? "bg-zinc-200/70 text-ink-primary font-medium"
                                    : "text-ink-muted hover:bg-zinc-200/50",
                                isCollapsed && "justify-center px-0"
                            )}
                            title={isCollapsed ? item.label : undefined}
                        >
                            <item.icon size={18} className="shrink-0" />
                            {!isCollapsed && <span>{item.label}</span>}

                            {/* Tooltip for collapsed state */}
                            {isCollapsed && (
                                <div className="absolute left-full ml-2 px-2 py-1 bg-zinc-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                                    {item.label}
                                </div>
                            )}
                        </Link>
                    ))}
                </div>

            </div>

            {/* 底部用户区 */}
            <div className="p-2 border-t border-hairline shrink-0 bg-paper z-10">
                <Link
                    href="/settings"
                    className={cn(
                        "w-full flex items-center gap-3 p-2 hover:bg-zinc-200/50 rounded-sm transition-colors text-left group relative",
                        isCollapsed && "justify-center"
                    )}
                    title={isCollapsed ? "Web3 Master" : undefined}
                >
                    <div className="w-8 h-8 bg-zinc-300 rounded-full flex items-center justify-center text-xs font-serif text-ink-primary shrink-0">
                        QS
                    </div>
                    {!isCollapsed && (
                        <>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm font-medium truncate text-ink-primary">Web3 Master</div>
                            </div>
                            <Settings size={14} className="text-ink-muted" />
                        </>
                    )}

                    {/* Tooltip for collapsed state */}
                    {isCollapsed && (
                        <div className="absolute left-full ml-2 px-2 py-1 bg-zinc-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                            Web3 Master
                        </div>
                    )}
                </Link>
            </div>
        </aside>
    );
}
