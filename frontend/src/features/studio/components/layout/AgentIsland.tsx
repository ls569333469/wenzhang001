'use client';

import { IslandContainer } from "./IslandContainer";
import { Activity } from "lucide-react";
import { AgentTimeline } from "../timeline/AgentTimeline";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { UI_TEXT } from "@/config/constants";

/**
 * AgentIsland - 右侧智能体岛
 * 
 * 职责:
 * 1. 展示 Agent 思考流 (From useAgentStore)
 * 2. 状态指示器
 */
export function AgentIsland() {
    const { steps, status } = useAgentStore();
    const isActive = status === 'thinking' || status === 'writing' || status === 'connecting';

    return (
        <IslandContainer position="right">
            {/* Header */}
            <div className="p-4 border-b border-zinc-50 bg-zinc-50/30 backdrop-blur pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary" />
                        <h3 className="text-sm font-semibold text-ink-primary">{UI_TEXT.agentFlow.title}</h3>
                    </div>
                    {/* Active Logic: Show pulsing green dot if active */}
                    <span className="flex h-2 w-2">
                        {isActive && (
                            <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                        )}
                        <span className={`relative inline-flex rounded-full h-2 w-2 ${isActive ? 'bg-green-500' : 'bg-zinc-300'}`}></span>
                    </span>
                </div>
            </div>

            {/* Timeline Content */}
            <div className="flex-1 p-4 overflow-y-auto">
                <AgentTimeline steps={steps} />
            </div>
        </IslandContainer>
    );
}
