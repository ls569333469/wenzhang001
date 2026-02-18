'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { StudioLayout } from "@/features/studio/layout/StudioLayout";
import { ConfigIsland } from "@/features/studio/components/layout/ConfigIsland";
import { UnifiedSidebar } from "@/features/studio/components/sidebar/UnifiedSidebar";
import { WritingCanvas } from "@/features/studio/components/WritingCanvas";
import { MaterialCenter } from "@/features/studio/components/MaterialCenter";
import { CreationHistory } from "@/features/studio/components/CreationHistory";
// DetailPanel deprecated in P19 Phase 2

/**
 * Studio Page - 组装页
 * 
 * P10-9: DetailPanel replaced by UnifiedSidebar Tabs
 * P14-C: 添加 Suspense 边界以支持 nuqs useSearchParams
 * P23: 素材中心作为 ?view=materials Tab
 * P27: 创作历史作为 ?view=history Tab
 */

function StudioContent() {
    const searchParams = useSearchParams();
    const view = searchParams.get('view');

    // P23: 素材中心视图 — 全宽, 无左右面板
    if (view === 'materials') {
        return (
            <StudioLayout>
                <MaterialCenter />
            </StudioLayout>
        );
    }

    // P27: 创作历史视图
    if (view === 'history') {
        return (
            <StudioLayout>
                <CreationHistory />
            </StudioLayout>
        );
    }

    // 默认: 创作视图
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
