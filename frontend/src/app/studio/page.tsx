'use client';

import { Suspense } from 'react';
import { StudioLayout } from "@/features/studio/layout/StudioLayout";
import { ConfigIsland } from "@/features/studio/components/layout/ConfigIsland";
import { AgentIsland } from "@/features/studio/components/layout/AgentIsland";
import { WritingCanvas } from "@/features/studio/components/WritingCanvas";
import { DetailPanel, DetailPanelProvider } from "@/features/studio/components/DetailPanel";

/**
 * Studio Page - 组装页
 * 
 * P10-9: 添加 DetailPanelProvider 支持滑出面板
 * P14-C: 添加 Suspense 边界以支持 nuqs useSearchParams
 */

function StudioContent() {
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

export default function StudioPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center">加载中...</div>}>
            <StudioContent />
        </Suspense>
    );
}

