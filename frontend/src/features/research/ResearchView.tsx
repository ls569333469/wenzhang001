'use client';

import { useState, useEffect } from 'react';
import { CardPreview } from './CardPreview';
import { TweetCards } from './TweetCards';
import { ReportSection } from './ReportSection';
import { RefreshCw, AlertCircle } from 'lucide-react';

interface ResearchData {
    date: string;
    project_count: number;
    card_html: string | null;
    tweets: { name: string; text: string; char_count: number }[];
    report_md: string | null;
}

export function ResearchView() {
    const [data, setData] = useState<ResearchData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/api/research/latest');
            if (!res.ok) {
                if (res.status === 404) {
                    setError('暂无投研报告，请先运行 Pipeline 生成');
                    return;
                }
                throw new Error(`API 错误: ${res.status}`);
            }
            const json = await res.json();
            setData(json);
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '加载失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-canvas">
                <div className="flex items-center gap-3 text-ink-muted">
                    <RefreshCw size={18} className="animate-spin" />
                    <span>加载投研报告...</span>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-canvas p-8">
                <div className="text-center max-w-md space-y-4">
                    <AlertCircle size={48} className="mx-auto text-zinc-400" />
                    <h2 className="text-xl font-serif font-bold text-ink-primary">投研报告</h2>
                    <p className="text-ink-muted text-sm">{error || '暂无数据'}</p>
                    <button
                        onClick={fetchData}
                        className="px-4 py-2 text-sm font-medium bg-zinc-900 text-white rounded-xl hover:bg-zinc-800 transition-colors"
                    >
                        重新加载
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto bg-canvas">
            <div className="w-full mx-auto p-4 space-y-4">
                {/* 页面头部 */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-xl font-serif font-bold text-ink-primary">
                            📊 投研快报
                        </h1>
                        <p className="text-sm text-ink-muted mt-1">
                            {data.date} · {data.project_count} 个项目
                        </p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="flex items-center gap-2 px-3 py-1.5 text-sm text-ink-muted hover:text-ink-primary border border-zinc-200 rounded-lg hover:bg-zinc-50 transition-colors"
                    >
                        <RefreshCw size={14} />
                        刷新
                    </button>
                </div>

                {/* 区域 1: 配图预览 */}
                {data.card_html && (
                    <CardPreview html={data.card_html} date={data.date} />
                )}

                {/* 区域 2: 推文文案 */}
                {data.tweets.length > 0 && (
                    <TweetCards tweets={data.tweets} />
                )}

                {/* 区域 3: 完整报告 */}
                {data.report_md && (
                    <ReportSection markdown={data.report_md} />
                )}
            </div>
        </div>
    );
}
