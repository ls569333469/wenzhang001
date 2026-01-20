'use client';

import React from "react";
import { LayoutGrid, FileText, Settings, PenTool, Brain } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function AdaptiveSidebar() {
    const pathname = usePathname();

    const navItems = [
        { href: "/dashboard", icon: LayoutGrid, label: "仪表盘" },
        { href: "/studio", icon: PenTool, label: "创作工坊" },
        { href: "/knowledge", icon: Brain, label: "知识库" },
        { href: "/settings", icon: Settings, label: "系统设置" },
    ];

    return (
        <aside className="w-[280px] h-full flex flex-col border-r border-hairline bg-paper text-ink-primary overflow-hidden">
            {/* 顶部固定区 */}
            <div className="h-14 flex items-center px-4 border-b border-hairline shrink-0">
                <div>
                    <h1 className="text-base font-serif font-medium text-ink-primary">量子工坊</h1>
                    <p className="text-[10px] text-ink-muted uppercase tracking-wider">v6.1 — 雅典娜殿堂</p>
                </div>
            </div>

            {/* 滚动内容区 - 无搜索框 (Clean UI) */}
            <div className="flex-1 overflow-y-auto p-3 space-y-6">
                {/* 导航菜单 */}
                <div className="space-y-1">
                    <div className="px-2 text-[10px] font-semibold text-ink-muted uppercase tracking-wider mb-2">
                        导航
                    </div>
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "w-full flex items-center gap-3 px-2 py-2 text-sm rounded-sm transition-colors text-left",
                                pathname === item.href
                                    ? "bg-zinc-200/70 text-ink-primary font-medium"
                                    : "text-ink-muted hover:bg-zinc-200/50"
                            )}
                        >
                            <item.icon size={16} />
                            <span>{item.label}</span>
                        </Link>
                    ))}
                </div>

                {/* 最近项目 */}
                <div className="space-y-1">
                    <div className="px-2 text-[10px] font-semibold text-ink-muted uppercase tracking-wider mb-2">
                        最近项目
                    </div>
                    <button className="w-full flex items-center gap-3 px-2 py-2 text-sm text-ink-muted hover:bg-zinc-200/50 rounded-sm transition-colors text-left">
                        <FileText size={16} />
                        <span>DeFi 周报 (草稿)</span>
                    </button>
                    <button className="w-full flex items-center gap-3 px-2 py-2 text-sm text-ink-muted hover:bg-zinc-200/50 rounded-sm transition-colors text-left">
                        <FileText size={16} />
                        <span>Layer 2 深度分析</span>
                    </button>
                </div>
            </div>

            {/* 底部用户区 - 无"免费版"文字 (Clean UI) */}
            <div className="p-3 border-t border-hairline shrink-0 bg-paper z-10">
                <Link
                    href="/settings"
                    className="w-full flex items-center gap-3 p-2 hover:bg-zinc-200/50 rounded-sm transition-colors text-left"
                >
                    <div className="w-8 h-8 bg-zinc-300 rounded-full flex items-center justify-center text-xs font-serif text-ink-primary">
                        QS
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate text-ink-primary">Web3 Master</div>
                    </div>
                    <Settings size={14} className="text-ink-muted" />
                </Link>
            </div>
        </aside>
    );
}
