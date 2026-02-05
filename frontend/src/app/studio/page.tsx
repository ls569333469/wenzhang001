'use client';

import { Suspense } from 'react';
import { StudioLayout } from "@/features/studio/layout/StudioLayout";
import { ConfigIsland } from "@/features/studio/components/layout/ConfigIsland";
import { UnifiedSidebar } from "@/features/studio/components/sidebar/UnifiedSidebar";
import { WritingCanvas } from "@/features/studio/components/WritingCanvas";
// DetailPanel deprecated in P19 Phase 2

/**
 * Studio Page - 组装页
 * 
 * P10-9: DetailPanel replaced by UnifiedSidebar Tabs
 * P14-C: 添加 Suspense 边界以支持 nuqs useSearchParams
 */

function StudioContent() {
    return (
        <StudioLayout
            leftPanel={<ConfigIsland />}
            rightPanel={<UnifiedSidebar />}
        >
            {/* Layer 1: Central Canvas Content (Client Component) */}
            <WritingCanvas />
        </StudioLayout>
    );
}

export default function StudioPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center">加载中...</div>}>
            <StudioContent />
        </Suspense>
    );
}

