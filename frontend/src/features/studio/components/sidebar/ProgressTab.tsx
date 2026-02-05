'use client';

import { AgentTimeline } from "../timeline/AgentTimeline";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { toast } from "sonner";

export function ProgressTab() {
    const { steps, agentLogs } = useAgentStore();

    const handleViewThinking = () => {
        // Feature reverted/disabled
        toast.info("思维链功能暂时不可用");
    };

    return (
        <div className="space-y-4">
            <div className="text-sm font-semibold text-ink-primary mb-2">
                智能体执行进度
            </div>
            <AgentTimeline
                steps={steps}
                agentLogs={agentLogs}
            // onViewThinking={handleViewThinking} // Disabled for now
            />
        </div>
    );
}
