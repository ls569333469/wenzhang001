'use client';

import { StudioLayout } from "@/features/studio/layout/StudioLayout";
import { ConfigIsland } from "@/features/studio/components/layout/ConfigIsland";
import { AgentIsland } from "@/features/studio/components/layout/AgentIsland";
import { WritingCanvas } from "@/features/studio/components/WritingCanvas";
import { DetailPanel, DetailPanelProvider } from "@/features/studio/components/DetailPanel";

/**
 * Studio Page - 组装页
 * 
 * P10-9: 添加 DetailPanelProvider 支持滑出面板
 */
export default function StudioPage() {
    return (
        <DetailPanelProvider>
            <StudioLayout
                leftPanel={<ConfigIsland />}
                rightPanel={<AgentIsland />}
            >
                {/* Layer 1: Central Canvas Content (Client Component) */}
                <WritingCanvas />
            </StudioLayout>

            {/* P10-9: Slide-out Detail Panel */}
            <DetailPanel />
        </DetailPanelProvider>
    );
}
