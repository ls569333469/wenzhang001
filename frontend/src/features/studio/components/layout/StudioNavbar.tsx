'use client';

import { Sparkles, Search, BookOpen, Bot } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * StudioNavbar - 顶部导航岛
 * 
 * 形态: Pill Shape (胶囊)
 * 位置: Top Center Fixed
 */
export function StudioNavbar() {
    return (
        <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-top-4 duration-500">
            <div className="flex items-center gap-1 p-1.5 bg-white rounded-full shadow-island border border-zinc-100 ring-1 ring-zinc-50/50">

                {/* Logo / Home */}
                <button className="px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-medium flex items-center gap-2 shadow-sm hover:bg-zinc-800 transition-colors">
                    <Sparkles className="w-4 h-4" />
                    <span className="font-serif tracking-wide">Studio</span>
                </button>

                {/* Nav Links */}
                <NavPill label="Knowledge" icon={BookOpen} />
                <NavPill label="Agents" icon={Bot} />

                <div className="w-px h-4 bg-zinc-200 mx-1" />

                {/* Actions */}
                <button className="p-2 text-ink-muted hover:text-ink-primary rounded-full hover:bg-zinc-50 transition-colors">
                    <Search className="w-4 h-4" />
                </button>
            </div>
        </nav>
    );
}

function NavPill({ label, icon: Icon }: { label: string, icon: any }) {
    return (
        <button className="px-4 py-2 text-ink-muted hover:text-ink-primary hover:bg-zinc-50 rounded-full text-sm font-medium transition-colors flex items-center gap-2">
            {/* <Icon className="w-3.5 h-3.5 opacity-70" /> */}
            {label}
        </button>
    )
}
