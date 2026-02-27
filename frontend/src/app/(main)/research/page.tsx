'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * P31: 投研报告页面 → 重定向到 Studio 投研模式
 * 投研报告现在在 Studio 主区域展示
 */
export default function ResearchPage() {
    const router = useRouter();

    useEffect(() => {
        router.replace('/studio?mode=project_research');
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-ink-muted text-sm">跳转到投研工作台...</div>
        </div>
    );
}
