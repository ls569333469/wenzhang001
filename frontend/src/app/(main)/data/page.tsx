'use client';

/**
 * /data 数据管理 — 临时重定向页
 * 
 * P27: 导航栏指向 /data，但实际页面尚未构建
 * 暂时提供占位信息 + 跳转到知识库
 */

import Link from 'next/link';

export default function DataPage() {
    return (
        <div className="min-h-screen bg-canvas flex items-center justify-center p-8">
            <div className="text-center max-w-md space-y-6">
                <div className="text-5xl">📁</div>
                <h1 className="text-2xl font-serif font-bold text-ink-primary">数据管理</h1>
                <p className="text-ink-muted text-sm leading-relaxed">
                    此页面正在建设中。数据管理将整合知识库和数据清洗功能。
                </p>
                <div className="flex gap-3 justify-center">
                    <Link
                        href="/knowledge"
                        className="px-4 py-2 text-sm font-medium bg-zinc-900 text-white rounded-xl hover:bg-zinc-800 transition-colors"
                    >
                        前往知识库
                    </Link>
                    <Link
                        href="/studio"
                        className="px-4 py-2 text-sm font-medium bg-white text-ink-primary border border-zinc-200 rounded-xl hover:bg-zinc-50 transition-colors"
                    >
                        返回创作中心
                    </Link>
                </div>
            </div>
        </div>
    );
}
