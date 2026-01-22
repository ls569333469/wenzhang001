'use client';

import { useState } from 'react';
import { Check, Loader2, Sparkles, AlertCircle, ChevronDown, ChevronRight, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import { UI_TEXT } from "@/config/constants";

// 临时定义，后续从 schema 或 types 导入
export type TimelineStepStatus = 'idle' | 'thinking' | 'active' | 'completed' | 'error';
export type AgentType = 'strategist' | 'researcher' | 'writer' | 'critic' | 'polisher';

// P10-4: Sub-step for detailed progress
export interface SubStep {
    id: string;
    text: string;
    timestamp?: string;
}

export interface TimelineStep {
    id: string;
    agent: AgentType;
    label: string;
    status: TimelineStepStatus;
    message?: string;
    duration?: string;
    // P10-4: Enhanced fields
    subSteps?: SubStep[];
    logs?: string[];
}

interface AgentTimelineProps {
    steps: TimelineStep[];
    agentLogs?: string[];  // Global logs from store
    onViewThinking?: () => void; // P10-9: Trigger detail panel
}

/**
 * AgentTimeline - 智能体协作时间轴
 * 
 * P10-4 Enhanced:
 * - 可展开的子步骤显示
 * - 实时日志流
 * - 思考过程摘要
 */
export function AgentTimeline({ steps, agentLogs = [], onViewThinking }: AgentTimelineProps) {
    return (
        <div className="relative pl-2 space-y-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-px before:bg-zinc-100">
            {steps.map((step, index) => (
                <TimelineItem
                    key={step.id}
                    step={step}
                    isLast={index === steps.length - 1}
                    onViewThinking={onViewThinking}
                    logs={agentLogs.filter(log => log.toLowerCase().includes(step.agent))}
                />
            ))}
        </div>
    );
}

interface TimelineItemProps {
    step: TimelineStep;
    isLast: boolean;
    onViewThinking?: () => void;
    logs?: string[];
}

function TimelineItem({ step, isLast, onViewThinking, logs = [] }: TimelineItemProps) {
    const [isExpanded, setIsExpanded] = useState(false);

    const isActive = step.status === 'active' || step.status === 'thinking';
    const isCompleted = step.status === 'completed';
    const isError = step.status === 'error';
    const isStrategist = step.agent === 'strategist';

    const hasDetails = (step.subSteps && step.subSteps.length > 0) ||
        (step.logs && step.logs.length > 0) ||
        logs.length > 0;

    return (
        <div className={cn(
            "relative flex gap-4 group",
            isActive && "opacity-100",
            !isActive && !isCompleted && "opacity-50"
        )}>

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
                    <div className="flex items-center gap-2">
                        <span className={cn(
                            "text-xs font-semibold tracking-wide uppercase transition-colors",
                            isActive ? "text-primary" : "text-ink-secondary"
                        )}>
                            {step.label}
                        </span>

                        {/* P10-4: Expand/Collapse button */}
                        {(isCompleted || isActive) && hasDetails && (
                            <button
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="p-0.5 text-zinc-400 hover:text-zinc-600 transition-colors"
                                title={isExpanded ? "收起详情" : "展开详情"}
                            >
                                {isExpanded ? (
                                    <ChevronDown className="w-3.5 h-3.5" />
                                ) : (
                                    <ChevronRight className="w-3.5 h-3.5" />
                                )}
                            </button>
                        )}
                    </div>

                    {step.duration && (
                        <span className="text-[10px] font-mono text-ink-muted">{step.duration}</span>
                    )}
                </div>

                {/* Message / Status Text */}
                <div className="text-sm text-ink-primary leading-snug">
                    {step.status === 'thinking' && (
                        <div className="flex items-center gap-2 text-ink-muted italic">
                            <Sparkles className="w-3 h-3 animate-pulse" />
                            <span>{step.message || UI_TEXT.status.thinking}</span>
                        </div>
                    )}
                    {step.status === 'active' && (
                        <div className="flex items-center gap-2">
                            <Loader2 className="w-3 h-3 animate-spin text-primary" />
                            <span>{step.message || UI_TEXT.status.processing}</span>
                        </div>
                    )}
                    {isCompleted && (
                        <span className="text-ink-secondary">{step.message || UI_TEXT.status.completed}</span>
                    )}
                    {step.status === 'idle' && (
                        <span className="text-ink-muted">{UI_TEXT.status.idle}</span>
                    )}
                </div>

                {/* P10-4: Expanded Details Section */}
                {isExpanded && (
                    <div className="mt-3 space-y-2 animate-in slide-in-from-top-2 duration-200">
                        {/* Sub-steps */}
                        {step.subSteps && step.subSteps.length > 0 && (
                            <div className="pl-2 border-l-2 border-zinc-100 space-y-1">
                                {step.subSteps.map((sub, idx) => (
                                    <div key={sub.id || idx} className="flex items-center gap-2 text-xs text-zinc-500">
                                        <div className="w-1 h-1 rounded-full bg-zinc-300" />
                                        <span>{sub.text}</span>
                                        {sub.timestamp && (
                                            <span className="text-zinc-400 font-mono">{sub.timestamp}</span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Logs */}
                        {(step.logs && step.logs.length > 0) || logs.length > 0 ? (
                            <div className="bg-zinc-50 rounded-lg p-2 space-y-1 max-h-32 overflow-y-auto">
                                <div className="flex items-center gap-1.5 text-xs font-medium text-zinc-500 mb-1.5">
                                    <MessageSquare className="w-3 h-3" />
                                    <span>执行日志</span>
                                </div>
                                {(step.logs || logs).map((log, idx) => (
                                    <div key={idx} className="text-[11px] font-mono text-zinc-600 leading-relaxed">
                                        {log}
                                    </div>
                                ))}
                            </div>
                        ) : null}
                    </div>
                )}

                {/* P10-9: View Thinking Chain Link (only for completed strategist) */}
                {isCompleted && isStrategist && onViewThinking && (
                    <button
                        onClick={onViewThinking}
                        className="mt-2 text-xs text-blue-500 hover:text-blue-600 hover:underline"
                    >
                        查看思维链 →
                    </button>
                )}
            </div>

        </div>
    );
}


