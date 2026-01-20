'use client'

import * as React from 'react'
import Link from 'next/link'
import { cn } from "@/lib/utils"
import { ArrowRight } from 'lucide-react'

interface ActionTileProps {
    href: string
    icon: React.ElementType
    label: string
    variant?: 'primary' | 'secondary'
    className?: string
}

/**
 * ActionTile: Standard action button/link for Paper Mode v6.0
 * Eliminates default browser link styling (blue/purple underlines)
 * Specs: flex items-center gap-3 p-4 border border-zinc-200 hover:bg-zinc-50 rounded-sm
 */
export function ActionTile({ href, icon: Icon, label, variant = 'primary', className }: ActionTileProps) {
    const isPrimary = variant === 'primary'

    return (
        <Link
            href={href}
            className={cn(
                "flex items-center gap-3 px-5 py-3 rounded-sm transition-colors group",
                isPrimary
                    ? "bg-zinc-800 hover:bg-zinc-700"
                    : "border border-hairline bg-surface hover:bg-zinc-50 hover:border-zinc-300",
                className
            )}
            style={{ textDecoration: 'none', color: 'inherit' }}
        >
            <Icon className={cn("w-4 h-4", isPrimary ? "text-zinc-50" : "text-zinc-600")} />
            <span className={cn("text-sm font-medium", isPrimary ? "text-zinc-50" : "text-zinc-800")}>
                {label}
            </span>
            <ArrowRight className={cn(
                "w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity",
                isPrimary ? "text-zinc-50" : "text-zinc-600"
            )} />
        </Link>
    )
}
