'use client';

import { Check, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

// 临时定义，后续从 schema 或 types 导入
export type TimelineStepStatus = 'idle' | 'thinking' | 'active' | 'completed' | 'error';
export type AgentType = 'strategist' | 'researcher' | 'writer' | 'critic';

export interface TimelineStep {
    id: string;
    agent: AgentType;
    label: string;
    status: TimelineStepStatus;
    message?: string;
    duration?: string;
}

interface AgentTimelineProps {
    steps: TimelineStep[];
}

/**
 * AgentTimeline - 智能体协作时间轴
 * 
 * 视觉风格: 
 * - 连接线 (Timeline thread)
 * - 脉冲节点 (Pulsing dots for active state)
 * - 极简排版
 */
export function AgentTimeline({ steps }: AgentTimelineProps) {
    return (
        <div className="relative pl-2 space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-px before:bg-zinc-100">
            {steps.map((step, index) => (
                <TimelineItem key={step.id} step={step} isLast={index === steps.length - 1} />
            ))}
        </div>
    );
}

function TimelineItem({ step, isLast }: { step: TimelineStep, isLast: boolean }) {
    const isActive = step.status === 'active' || step.status === 'thinking';
    const isCompleted = step.status === 'completed';
    const isError = step.status === 'error';

    return (
        <div className={cn("relative flex gap-4 group", isActive && "opacity-100", !isActive && !isCompleted && "opacity-50")}>

            {/* 1. Node Icon */}
            <div className={cn(
                "relative z-10 flex items-center justify-center w-5 h-5 rounded-full border bg-white transition-all duration-300",
                isActive ? "border-primary ring-2 ring-primary/10 scale-110" : "border-zinc-200",
                isCompleted ? "bg-primary border-primary text-white" : "",
                isError ? "border-red-500 bg-red-50" : ""
            )}>
                {isCompleted && <Check className="w-3 h-3" />}
                {isActive && <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />}
                {isError && <AlertCircle className="w-3 h-3 text-red-500" />}
                {step.status === 'idle' && <div className="w-1.5 h-1.5 bg-zinc-300 rounded-full" />}
            </div>

            {/* 2. Content */}
            <div className="flex-1 pt-0.5">
                <div className="flex items-center justify-between mb-1">
                    <span className={cn(
                        "text-xs font-semibold tracking-wide uppercase transition-colors",
                        isActive ? "text-primary" : "text-ink-secondary"
                    )}>
                        {step.label}
                    </span>
                    {step.duration && (
                        <span className="text-[10px] font-mono text-ink-muted">{step.duration}</span>
                    )}
                </div>

                {/* Message / Status Text */}
                <div className="text-sm text-ink-primary leading-snug">
                    {step.status === 'thinking' && (
                        <div className="flex items-center gap-2 text-ink-muted italic">
                            <Sparkles className="w-3 h-3 animate-pulse" />
                            <span>{step.message || '思考中...'}</span>
                        </div>
                    )}
                    {step.status === 'active' && (
                        <div className="flex items-center gap-2">
                            <Loader2 className="w-3 h-3 animate-spin text-primary" />
                            <span>{step.message || 'Processing...'}</span>
                        </div>
                    )}
                    {isCompleted && (
                        <span className="text-ink-secondary">{step.message || 'Completed'}</span>
                    )}
                    {step.status === 'idle' && (
                        <span className="text-ink-muted">Waiting to start</span>
                    )}
                </div>
            </div>

        </div>
    );
}
