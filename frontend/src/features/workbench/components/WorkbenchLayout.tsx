'use client'

import React from 'react'
import { SidebarConfig } from './SidebarConfig'
import { WritingCanvas } from './WritingCanvas'
import { AgentInspector } from './AgentInspector'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { Zap, RotateCcw, Settings2 } from 'lucide-react'
import { useGeneration } from '../hooks/useGeneration'

export function WorkbenchLayout() {
    const { resetFlow } = useGeneration()

    return (
        <div className="h-screen bg-background flex flex-col overflow-hidden font-sans text-sm antialiased text-foreground">
            {/* Header - Linear Style: Low height, subtle border */}
            <header className="h-12 border-b bg-card/50 backdrop-blur-sm px-4 flex items-center justify-between shrink-0 z-20 sticky top-0">
                <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded bg-primary/10 flex items-center justify-center">
                        <Zap className="w-4 h-4 text-primary" />
                    </div>
                    <span className="font-semibold text-foreground tracking-tight">Quantum Studio</span>
                    <span className="text-xs text-muted-foreground px-1.5 py-0.5 rounded-md bg-secondary border">v5.1 Pro</span>
                </div>
                <div className="flex gap-2">
                    <Button variant="ghost" size="sm" onClick={resetFlow} className="gap-2">
                        <RotateCcw className="w-4 h-4" />
                        Reset Flow
                    </Button>
                    <Link href="/settings">
                        <Button variant="ghost" size="sm" className="gap-2">
                            <Settings2 className="w-4 h-4" />
                            Settings
                        </Button>
                    </Link>
                </div>
            </header>

            {/* Main Content - Option A: Classic Three Column */}
            <main className="flex-1 grid grid-cols-12 overflow-hidden">
                <SidebarConfig />
                <WritingCanvas />
                <AgentInspector />
            </main>
        </div>
    )
}
