import React from "react";
import { ArrowRight, LucideIcon } from "lucide-react";
import Link from "next/link";

interface ActionTileProps {
    icon: LucideIcon;
    title: string;
    description: string;
    href: string;
}

export function ActionTile({ icon: Icon, title, description, href }: ActionTileProps) {
    return (
        <Link
            href={href}
            className="group flex flex-col justify-between p-5 bg-white border border-zinc-200 rounded-sm hover:border-zinc-300 hover:shadow-sm transition-all duration-200"
        >
            <div>
                <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 flex items-center justify-center rounded-sm bg-zinc-100 text-zinc-600 group-hover:bg-zinc-800 group-hover:text-white transition-colors">
                        <Icon size={18} strokeWidth={1.5} />
                    </div>
                    <ArrowRight
                        size={16}
                        className="text-zinc-300 group-hover:text-zinc-600 group-hover:translate-x-1 transition-all"
                    />
                </div>
                <h3 className="text-base font-serif font-medium text-zinc-800 mb-1">
                    {title}
                </h3>
                <p className="text-xs text-zinc-500 leading-relaxed">
                    {description}
                </p>
            </div>
        </Link>
    );
}
