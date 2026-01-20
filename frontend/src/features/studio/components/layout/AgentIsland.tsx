import { IslandContainer } from "./IslandContainer";
import { Activity } from "lucide-react";
import { AgentTimeline, TimelineStep } from "../timeline/AgentTimeline";

// Mock Data for Verification
const MOCK_STEPS: TimelineStep[] = [
    { id: '1', agent: 'strategist', label: 'Strategy', status: 'completed', message: 'Analyzed user intent: Deep Research', duration: '1.2s' },
    { id: '2', agent: 'researcher', label: 'Research', status: 'active', message: 'Searching knowledge base...', duration: '0.5s' },
    { id: '3', agent: 'writer', label: 'Drafting', status: 'idle', message: 'Waiting for research insights' },
    { id: '4', agent: 'critic', label: 'Review', status: 'idle', message: 'Pending draft' },
];

/**
 * AgentIsland - 右侧智能体岛
 * 
 * 职责:
 * 1. 展示 Agent 思考流
 * 2. 状态指示器
 */
export function AgentIsland() {
    return (
        <IslandContainer position="right">
            {/* Header */}
            <div className="p-4 border-b border-zinc-50 bg-zinc-50/30 backdrop-blur pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary" />
                        <h3 className="text-sm font-semibold text-ink-primary">Agent Flow</h3>
                    </div>
                    <span className="flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                </div>
            </div>

            {/* Timeline Content */}
            <div className="flex-1 p-4 overflow-y-auto">
                <AgentTimeline steps={MOCK_STEPS} />
            </div>
        </IslandContainer>
    );
}
