'use client';

import { useState, useEffect, useCallback } from 'react';
import { FileBarChart, ChevronDown, ChevronRight, Download, ExternalLink, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

interface DailyReport {
    type: string;
    date: string;
    date_raw: string;
    filename: string;
    summary: string;
    size: number;
}

interface ProjectReport {
    type: string;
    name: string;
    date_raw: string;
    filename: string;
    size: number;
}

/**
 * P31: 投研存档组件
 * 展示日报列表 + 项目深度报告
 * 调用 GET /api/research/reports
 */
export function ResearchArchive() {
    const [dailyReports, setDailyReports] = useState<DailyReport[]>([]);
    const [projectReports, setProjectReports] = useState<ProjectReport[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [expandedDaily, setExpandedDaily] = useState<string | null>(null);
    const [expandedProject, setExpandedProject] = useState<string | null>(null);
    const [dailyContent, setDailyContent] = useState<Record<string, string>>({});
    const [projectContent, setProjectContent] = useState<Record<string, string>>({});

    const fetchReports = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE_URL}/api/research/reports`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setDailyReports(data.daily_reports || []);
            setProjectReports(data.project_reports || []);
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '加载失败');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchReports(); }, [fetchReports]);

    // 展开日报 → 加载完整内容
    const toggleDaily = async (dateRaw: string, filename: string) => {
        if (expandedDaily === dateRaw) {
            setExpandedDaily(null);
            return;
        }
        setExpandedDaily(dateRaw);
        if (!dailyContent[dateRaw]) {
            try {
                const res = await fetch(`${API_BASE_URL}/api/research/latest?date=${dateRaw}`);
                if (res.ok) {
                    const data = await res.json();
                    setDailyContent(prev => ({ ...prev, [dateRaw]: data.report_md || '暂无内容' }));
                }
            } catch {
                setDailyContent(prev => ({ ...prev, [dateRaw]: '加载失败' }));
            }
        }
    };

    // 展开项目报告
    const toggleProject = async (filename: string) => {
        if (expandedProject === filename) {
            setExpandedProject(null);
            return;
        }
        setExpandedProject(filename);
        if (!projectContent[filename]) {
            try {
                const res = await fetch(`${API_BASE_URL}/api/research/project-report/${filename}`);
                if (res.ok) {
                    const data = await res.json();
                    setProjectContent(prev => ({ ...prev, [filename]: data.content || '暂无内容' }));
                } else {
                    setProjectContent(prev => ({ ...prev, [filename]: '暂无内容（API 待实现）' }));
                }
            } catch {
                setProjectContent(prev => ({ ...prev, [filename]: '加载失败' }));
            }
        }
    };

    // 下载 MD 文件
    const downloadMd = (content: string, filename: string) => {
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    const formatSize = (bytes: number) => {
        if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${bytes} B`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <Loader2 className="w-5 h-5 animate-spin text-zinc-400 mr-2" />
                <span className="text-sm text-ink-muted">加载投研报告...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-20">
                <p className="text-sm text-red-500">{error}</p>
                <button onClick={fetchReports} className="mt-3 text-sm text-primary underline">重试</button>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* 日报列表 */}
            <section>
                <h3 className="text-sm font-semibold text-ink-primary mb-3 flex items-center gap-2">
                    📅 日报列表
                    <span className="text-xs font-normal text-ink-muted">({dailyReports.length} 份)</span>
                </h3>
                <div className="bg-white rounded-xl border border-zinc-100 divide-y divide-zinc-100">
                    {dailyReports.length === 0 ? (
                        <div className="p-8 text-center text-sm text-ink-muted">暂无日报</div>
                    ) : (
                        dailyReports.map((report) => (
                            <div key={report.date_raw}>
                                <button
                                    onClick={() => toggleDaily(report.date_raw, report.filename)}
                                    className="w-full flex items-center justify-between p-4 hover:bg-zinc-50 transition-colors text-left"
                                >
                                    <div className="flex items-center gap-3">
                                        {expandedDaily === report.date_raw ? (
                                            <ChevronDown className="w-4 h-4 text-zinc-400" />
                                        ) : (
                                            <ChevronRight className="w-4 h-4 text-zinc-400" />
                                        )}
                                        <div>
                                            <span className="text-sm font-medium text-ink-primary">{report.date}</span>
                                            <p className="text-xs text-ink-muted mt-0.5 line-clamp-1 max-w-md">
                                                {report.summary}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs text-ink-muted">{formatSize(report.size)}</span>
                                    </div>
                                </button>
                                {expandedDaily === report.date_raw && (
                                    <div className="px-4 pb-4">
                                        <div className="flex gap-2 mb-3">
                                            {dailyContent[report.date_raw] && (
                                                <button
                                                    onClick={() => downloadMd(dailyContent[report.date_raw], report.filename)}
                                                    className="flex items-center gap-1 px-3 py-1.5 text-xs border border-zinc-200 rounded-lg hover:bg-zinc-50 transition-colors"
                                                >
                                                    <Download className="w-3 h-3" /> 下载 MD
                                                </button>
                                            )}
                                            <a
                                                href="/studio?mode=project_research"
                                                className="flex items-center gap-1 px-3 py-1.5 text-xs border border-zinc-200 rounded-lg hover:bg-zinc-50 transition-colors"
                                            >
                                                <ExternalLink className="w-3 h-3" /> 在 Studio 打开
                                            </a>
                                        </div>
                                        <div className="bg-zinc-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                                            <pre className="text-xs text-ink-primary whitespace-pre-wrap font-mono leading-relaxed">
                                                {dailyContent[report.date_raw] || '加载中...'}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </section>

            {/* 项目深度报告 */}
            <section>
                <h3 className="text-sm font-semibold text-ink-primary mb-3 flex items-center gap-2">
                    🔬 项目深度报告
                    <span className="text-xs font-normal text-ink-muted">({projectReports.length} 份)</span>
                </h3>
                <div className="bg-white rounded-xl border border-zinc-100 divide-y divide-zinc-100 max-h-[600px] overflow-y-auto">
                    {projectReports.length === 0 ? (
                        <div className="p-8 text-center text-sm text-ink-muted">暂无项目报告</div>
                    ) : (
                        projectReports.map((report) => (
                            <div key={report.filename}>
                                <button
                                    onClick={() => toggleProject(report.filename)}
                                    className="w-full flex items-center justify-between p-3 hover:bg-zinc-50 transition-colors text-left"
                                >
                                    <div className="flex items-center gap-3">
                                        {expandedProject === report.filename ? (
                                            <ChevronDown className="w-4 h-4 text-zinc-400" />
                                        ) : (
                                            <ChevronRight className="w-4 h-4 text-zinc-400" />
                                        )}
                                        <span className="text-sm text-ink-primary">{report.name}</span>
                                        {report.date_raw && (
                                            <span className="text-xs text-ink-muted">
                                                {report.date_raw.slice(0, 4)}-{report.date_raw.slice(4, 6)}-{report.date_raw.slice(6)}
                                            </span>
                                        )}
                                    </div>
                                    <span className="text-xs text-ink-muted">{formatSize(report.size)}</span>
                                </button>
                                {expandedProject === report.filename && (
                                    <div className="px-4 pb-3">
                                        <div className="bg-zinc-50 rounded-lg p-4 max-h-80 overflow-y-auto">
                                            <pre className="text-xs text-ink-primary whitespace-pre-wrap font-mono leading-relaxed">
                                                {projectContent[report.filename] || '加载中...'}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </section>
        </div>
    );
}
