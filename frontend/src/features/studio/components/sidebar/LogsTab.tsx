'use client';

import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { Terminal } from "lucide-react";

export function LogsTab() {
    const { agentLogs } = useAgentStore();

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-ink-primary mb-2">
                <Terminal className="w-4 h-4" />
                系统日志
            </div>

            {agentLogs.length === 0 ? (
                <div className="text-sm text-zinc-400 italic py-4 text-center">
                    暂无日志记录
                </div>
            ) : (
                <div className="space-y-1.5 font-mono text-xs">
                    {agentLogs.map((log, index) => (
                        <div key={index} className="bg-zinc-50 p-2 rounded border border-zinc-100 text-zinc-600 break-words leading-relaxed">
                            {log}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
