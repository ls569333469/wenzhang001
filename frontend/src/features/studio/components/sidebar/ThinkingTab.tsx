'use client';

import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { Brain } from "lucide-react";

export function ThinkingTab() {
    const { agentLogs, status } = useAgentStore();

    // Extract thinking content from logs (look for <think> tags)
    // Also consider streaming content if it's currently thinking
    const thinkingLog = agentLogs.find(log => log.includes('<think>')) || '';

    // Simple parser for now, effectively extracts content between tags
    const content = thinkingLog.replace(/<\/?think>/g, '').trim();

    return (
        <div className="space-y-4 h-full flex flex-col">
            <div className="text-sm font-semibold text-ink-primary flex items-center gap-2 shrink-0">
                <Brain className="w-4 h-4 text-green-600" />
                策略师思维链
            </div>

            <div className="flex-1 bg-zinc-900 rounded-lg p-4 font-mono text-xs leading-relaxed overflow-y-auto custom-scrollbar">
                {content ? (
                    <div className="whitespace-pre-wrap text-zinc-300">
                        <span className="text-green-500/50 select-none">&lt;think&gt;</span>
                        {'\n\n'}
                        {content}
                        {'\n\n'}
                        <span className="text-green-500/50 select-none">&lt;/think&gt;</span>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-600 space-y-2">
                        {status === 'thinking' ? (
                            <>
                                <Brain className="w-8 h-8 animate-pulse text-zinc-700" />
                                <span>AI 正在思考...</span>
                            </>
                        ) : (
                            <>
                                <Brain className="w-8 h-8 text-zinc-800" />
                                <span>暂无思考内容</span>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Hint */}
            <div className="text-[10px] text-zinc-400 text-center shrink-0 pt-2">
                * 展示 DeepSeek R1 / 策略师的原始思考过程
            </div>
        </div>
    );
}
