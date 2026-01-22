'use client';

import { IslandContainer } from "./IslandContainer";
import { AgentTimeline } from "../timeline/AgentTimeline";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { useDetailPanel } from "../DetailPanel";

/**
 * AgentIsland v3.1 - P10-4 Enhanced
 * 
 * 显示:
 * 1. 智能体进度时间轴 (4步)
 * 2. 可展开的子步骤和日志
 * 3. "[查看思维链→]" 链接
 */
export function AgentIsland() {
    const { steps, agentLogs } = useAgentStore();

    // Connect to DetailPanel
    let detailPanel: ReturnType<typeof useDetailPanel> | null = null;
    try {
        detailPanel = useDetailPanel();
    } catch {
        // Context not available
    }

    const handleViewThinking = () => {
        if (detailPanel) {
            detailPanel.openPanel('thinking');
        }
    };

    return (
        <IslandContainer position="right">
            <div className="p-4 h-full flex flex-col">
                {/* 标题 */}
                <div className="text-sm font-semibold text-ink-primary mb-4">
                    智能体进度
                </div>

                {/* 时间轴 */}
                <div className="flex-1 overflow-y-auto">
                    <AgentTimeline
                        steps={steps}
                        agentLogs={agentLogs}
                        onViewThinking={handleViewThinking}
                    />
                </div>

                {/* 查看思维链链接 */}
                <button
                    onClick={handleViewThinking}
                    className="mt-4 text-sm text-blue-500 hover:text-blue-600 hover:underline text-left"
                >
                    查看思维链 →
                </button>
            </div>
        </IslandContainer>
    );
}
