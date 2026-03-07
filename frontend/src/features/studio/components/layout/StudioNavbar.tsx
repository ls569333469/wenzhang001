'use client';

import { Sparkles, Search, FolderOpen, Home, Newspaper, History } from "lucide-react";
import { cn } from "@/lib/utils";
import { UI_TEXT } from "@/config/constants";
import Link from "next/link";

/**
 * StudioNavbar - 顶部导航岛
 * 
 * 形态: Pill Shape (胶囊)
 * 位置: Top Center Fixed
 * P27: [🏠] | [✨创作中心] [📁数据管理] [素材] [历史] [🔍]
 */
export function StudioNavbar() {
    return (
        <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
            <div className="flex items-center gap-1 p-1.5 bg-white rounded-full shadow-island border border-zinc-100 ring-1 ring-zinc-50/50">

                {/* Home / Dashboard */}
                <Link
                    href="/dashboard"
                    className="p-2 text-ink-muted hover:text-ink-primary rounded-full hover:bg-zinc-50 transition-colors"
                    title="返回主页"
                >
                    <Home className="w-4 h-4" />
                </Link>

                <div className="w-px h-4 bg-zinc-200 mx-1" />

                {/* 创作中心 (active) */}
                <button className="px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-medium flex items-center gap-2 shadow-sm hover:bg-zinc-800 transition-colors">
                    <Sparkles className="w-4 h-4" />
                    <span className="font-serif tracking-wide">{UI_TEXT.nav.studio}</span>
                </button>

                {/* Nav Links — P27: 知识库+清洗 → 数据管理 */}
                <NavPill label="数据中心" icon={FolderOpen} href="/data" />
                <NavPill label="素材" icon={Newspaper} href="/studio?view=materials" />
                <NavPill label="历史" icon={History} href="/studio?view=history" />

                <div className="w-px h-4 bg-zinc-200 mx-1" />

                {/* Actions */}
                <button className="p-2 text-ink-muted hover:text-ink-primary rounded-full hover:bg-zinc-50 transition-colors">
                    <Search className="w-4 h-4" />
                </button>
            </div>
        </nav>
    );
}

function NavPill({ label, icon: Icon, href }: { label: string, icon: any, href?: string }) {
    const content = (
        <span className="px-4 py-2 text-ink-muted hover:text-ink-primary hover:bg-zinc-50 rounded-full text-sm font-medium transition-colors flex items-center gap-2">
            {label}
        </span>
    );

    if (href) {
        return <Link href={href}>{content}</Link>;
    }
    return <button className="px-4 py-2 text-ink-muted hover:text-ink-primary hover:bg-zinc-50 rounded-full text-sm font-medium transition-colors flex items-center gap-2">{label}</button>;
}

