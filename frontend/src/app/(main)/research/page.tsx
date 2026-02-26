'use client';

import { Suspense } from 'react';
import { ResearchView } from '@/features/research/ResearchView';

/**
 * P31: 投研报告页面
 * 展示配图、推文文案和完整报告
 */
export default function ResearchPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-ink-muted">加载中...</div>
            </div>
        }>
            <ResearchView />
        </Suspense>
    );
}
