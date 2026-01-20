'use client'

import * as React from 'react'
import { cn } from "@/lib/utils"

interface PaperCardProps {
    children: React.ReactNode
    className?: string
    title?: string
    description?: string
}

/**
 * PaperCard: Standard card component for Paper Mode v6.0
 * Specs: bg-white rounded-sm border border-zinc-200 p-6
 */
export function PaperCard({ children, className, title, description }: PaperCardProps) {
    return (
        <div className={cn(
            "bg-surface rounded-sm border border-hairline p-6 shadow-sm",
            className
        )}>
            {title && (
                <h3 className="text-[10px] font-medium text-zinc-400 uppercase tracking-widest mb-4">
                    {title}
                </h3>
            )}
            {description && (
                <p className="text-xs text-zinc-500 mb-4">{description}</p>
            )}
            {children}
        </div>
    )
}
