'use client';

import Link from "next/link";
import { Sparkles, BookOpen, Bot, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Navbar Island - Fixed Top Navigation
 * 
 * Style: Floating island with shadow
 * Position: Fixed top, centered
 */

interface NavItem {
    id: string;
    label: string;
    icon: React.ElementType;
    href: string;
}

const navItems: NavItem[] = [
    { id: 'studio', label: '创作工坊', icon: Sparkles, href: '/studio' },
    { id: 'knowledge', label: '知识库', icon: BookOpen, href: '/knowledge' },
    { id: 'agents', label: 'AI 协作', icon: Bot, href: '/agents' },
];

interface NavbarProps {
    activeId?: string;
}

export function Navbar({ activeId = 'studio' }: NavbarProps) {
    return (
        <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50">
            <div className={cn(
                "flex items-center gap-1 px-2 py-1.5",
                "bg-island rounded-2xl shadow-island border border-zinc-100"
            )}>
                {/* Logo */}
                <Link
                    href="/"
                    className="flex items-center gap-2 px-3 py-2 mr-2"
                >
                    <div className="w-7 h-7 bg-primary rounded-lg flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <span className="font-serif font-semibold text-ink-primary">
                        量子工坊
                    </span>
                </Link>

                {/* Divider */}
                <div className="w-px h-6 bg-zinc-200" />

                {/* Nav Items */}
                <div className="flex items-center gap-1 ml-2">
                    {navItems.map((item) => (
                        <Link
                            key={item.id}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all",
                                activeId === item.id
                                    ? "bg-primary text-primary-foreground"
                                    : "text-ink-muted hover:text-ink-primary hover:bg-zinc-100"
                            )}
                        >
                            <item.icon className="w-4 h-4" />
                            <span>{item.label}</span>
                        </Link>
                    ))}
                </div>

                {/* Divider */}
                <div className="w-px h-6 bg-zinc-200 ml-2" />

                {/* Settings */}
                <Link
                    href="/settings"
                    className="p-2.5 ml-1 text-ink-muted hover:text-ink-primary hover:bg-zinc-100 rounded-xl transition-colors"
                >
                    <Settings className="w-4 h-4" />
                </Link>
            </div>
        </nav>
    );
}
