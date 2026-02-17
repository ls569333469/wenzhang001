'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    Newspaper, RefreshCw, ExternalLink, Star, Clock,
    Filter, Loader2, ArrowRight, Tag, Zap, FileText, ChevronDown
} from 'lucide-react';
import { API_BASE_URL } from '@/config/api';
import { cn } from '@/lib/utils';
import { useAgentStore } from '@/features/agent/stores/useAgentStore';
import { useRouter } from 'next/navigation';

// ==========================================
// Types
// ==========================================

interface MaterialItem {
    fetch_date: string;
    published_at: string;
    timeliness: string;
    source: string;
    content_type: string;
    title: string;
    url: string;
    content: string;
    summary: string;
    quality_score: number;
    score_reason: string;
    fact_type: string;
    keywords: string[];
    entities: string[];
    suggested_modes: string[];
    fingerprint: string;
    status: string;
}

interface MaterialStats {
    total: number;
    by_source: Record<string, number>;
    by_type: Record<string, number>;
    by_status: Record<string, number>;
    score_avg: number;
    fresh_count: number;
}

// ==========================================
// Sub-components
// ==========================================

function ScoreBadge({ score }: { score: number }) {
    const color = score >= 8 ? 'text-emerald-600 bg-emerald-50 border-emerald-200'
        : score >= 5 ? 'text-amber-600 bg-amber-50 border-amber-200'
            : 'text-zinc-500 bg-zinc-50 border-zinc-200';

    return (
        <span className={cn(
            "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border",
            color
        )}>
            <Star className="w-3 h-3" />
            {score}
        </span>
    );
}

function TimelinessBadge({ timeliness }: { timeliness: string }) {
    const map: Record<string, { label: string; className: string }> = {
        fresh: { label: '新鲜', className: 'text-green-600 bg-green-50' },
        recent: { label: '近期', className: 'text-blue-600 bg-blue-50' },
        stale: { label: '过期', className: 'text-zinc-400 bg-zinc-50' },
    };
    const info = map[timeliness] || { label: timeliness, className: 'text-zinc-400 bg-zinc-50' };

    return (
        <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs", info.className)}>
            <Clock className="w-3 h-3" />
            {info.label}
        </span>
    );
}

function MaterialCard({ item, onUseForCreation }: {
    item: MaterialItem;
    onUseForCreation: (item: MaterialItem) => void;
}) {
    const [expanded, setExpanded] = useState(false);

    return (
        <div className="group bg-white rounded-xl border border-zinc-100 hover:border-zinc-200 
                        hover:shadow-md transition-all duration-200 overflow-hidden">
            {/* Header */}
            <div className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                            <span className={cn(
                                "px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider",
                                item.content_type.includes('快讯')
                                    ? "bg-violet-50 text-violet-600"
                                    : "bg-sky-50 text-sky-600"
                            )}>
                                {item.content_type.includes('快讯') ? <Zap className="w-3 h-3 inline mr-0.5" /> : <FileText className="w-3 h-3 inline mr-0.5" />}
                                {item.content_type}
                            </span>
                            <ScoreBadge score={item.quality_score} />
                            <TimelinessBadge timeliness={item.timeliness} />
                        </div>

                        <h3 className="text-sm font-semibold text-zinc-900 leading-snug line-clamp-2 
                                       group-hover:text-zinc-700 transition-colors">
                            {item.title}
                        </h3>

                        {item.summary && (
                            <p className="mt-1.5 text-xs text-zinc-500 line-clamp-2">
                                {item.summary}
                            </p>
                        )}
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-1.5 shrink-0">
                        {item.url && (
                            <a href={item.url} target="_blank" rel="noopener noreferrer"
                                className="p-1.5 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-50 
                                          rounded-lg transition-colors"
                                title="原文链接">
                                <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                        )}
                    </div>
                </div>

                {/* Meta row */}
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <span className="text-[10px] text-zinc-400">
                        {item.source} · {item.published_at?.split('T')[0] || item.fetch_date}
                    </span>

                    {item.fact_type && (
                        <span className="px-1.5 py-0.5 bg-zinc-50 text-zinc-500 rounded text-[10px]">
                            {item.fact_type}
                        </span>
                    )}

                    {item.entities?.slice(0, 3).map((e, i) => (
                        <span key={i} className="px-1.5 py-0.5 bg-orange-50 text-orange-600 rounded text-[10px]">
                            {e}
                        </span>
                    ))}

                    {item.keywords?.slice(0, 2).map((k, i) => (
                        <span key={i} className="inline-flex items-center gap-0.5 text-[10px] text-zinc-400">
                            <Tag className="w-2.5 h-2.5" />{k}
                        </span>
                    ))}
                </div>
            </div>

            {/* Expandable content */}
            {expanded && item.content && (
                <div className="px-4 pb-3 border-t border-zinc-50">
                    <p className="text-xs text-zinc-600 leading-relaxed mt-3 whitespace-pre-line max-h-40 overflow-y-auto">
                        {item.content.slice(0, 500)}
                        {item.content.length > 500 && '...'}
                    </p>
                </div>
            )}

            {/* Footer */}
            <div className="px-4 py-2.5 bg-zinc-25 border-t border-zinc-50 flex items-center justify-between">
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="text-[11px] text-zinc-400 hover:text-zinc-600 flex items-center gap-1 transition-colors"
                >
                    <ChevronDown className={cn("w-3 h-3 transition-transform", expanded && "rotate-180")} />
                    {expanded ? '收起' : '展开正文'}
                </button>

                <div className="flex items-center gap-2">
                    {item.suggested_modes?.map((mode, i) => (
                        <span key={i} className="text-[10px] text-zinc-400 bg-zinc-50 px-1.5 py-0.5 rounded">
                            {mode}
                        </span>
                    ))}

                    <button
                        onClick={() => onUseForCreation(item)}
                        className={cn(
                            "flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                            item.status === '已创作'
                                ? "bg-zinc-100 text-zinc-400 cursor-default"
                                : "bg-zinc-900 text-white hover:bg-zinc-700 shadow-sm hover:shadow"
                        )}
                        disabled={item.status === '已创作'}
                    >
                        {item.status === '已创作' ? '已使用' : (
                            <>去创作 <ArrowRight className="w-3 h-3" /></>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}

// ==========================================
// Main Component
// ==========================================

export function MaterialCenter() {
    const [items, setItems] = useState<MaterialItem[]>([]);
    const [stats, setStats] = useState<MaterialStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [fetching, setFetching] = useState(false);
    const [filter, setFilter] = useState({
        content_type: '',
        min_score: 0,
        timeliness: '',
    });
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const router = useRouter();
    const { resetSession, setMaterialPrefill, setMaterialContext } = useAgentStore();

    const loadMaterials = useCallback(async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            params.set('page', page.toString());
            params.set('page_size', '20');
            if (filter.content_type) params.set('content_type', filter.content_type);
            if (filter.min_score) params.set('min_score', filter.min_score.toString());
            if (filter.timeliness) params.set('timeliness', filter.timeliness);

            const resp = await fetch(`${API_BASE_URL}/materials/list?${params}`);
            const data = await resp.json();

            setItems(data.items || []);
            setTotal(data.total || 0);
        } catch (err) {
            console.error('Failed to load materials:', err);
        } finally {
            setLoading(false);
        }
    }, [page, filter]);

    const loadStats = useCallback(async () => {
        try {
            const resp = await fetch(`${API_BASE_URL}/materials/stats`);
            const data = await resp.json();
            setStats(data);
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    }, []);

    useEffect(() => {
        loadMaterials();
        loadStats();
    }, [loadMaterials, loadStats]);

    const handleFetch = async () => {
        setFetching(true);
        try {
            const resp = await fetch(`${API_BASE_URL}/materials/fetch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source: 'chaincatcher', count: 10, analyze: true, analyze_count: 5 }),
            });
            const data = await resp.json();

            // Poll job status
            if (data.job_id) {
                const pollInterval = setInterval(async () => {
                    const statusResp = await fetch(`${API_BASE_URL}/materials/fetch/${data.job_id}`);
                    const statusData = await statusResp.json();

                    if (statusData.status === 'completed' || statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        setFetching(false);
                        loadMaterials();
                        loadStats();
                    }
                }, 3000);
            }
        } catch (err) {
            console.error('Fetch failed:', err);
            setFetching(false);
        }
    };

    const handleUseForCreation = async (item: MaterialItem) => {
        // 1. Reset session to idle
        resetSession();

        // 2. Input box: just the title as creation topic
        setMaterialPrefill(item.title);

        // 3. Full article content → separate context for backend strategist
        const fullContext = [
            item.summary || '',
            item.content || '',
            item.url ? `来源: ${item.url}` : '',
        ].filter(Boolean).join('\n\n');
        setMaterialContext(fullContext);

        // 4. Mark as used in backend (fire-and-forget)
        if (item.url) {
            fetch(`${API_BASE_URL}/materials/mark-used?url=${encodeURIComponent(item.url)}`, {
                method: 'POST'
            }).catch(() => { });
        }

        // 5. Navigate to studio with suggested mode
        const suggestedMode = item.suggested_modes?.[0] || 'deep_analysis';
        router.push(`/studio?mode=${suggestedMode}`);
    };

    const pageCount = Math.ceil(total / 20);

    return (
        <div className="w-full max-w-5xl mx-auto py-8 px-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-bold text-zinc-900 flex items-center gap-2">
                        <Newspaper className="w-5 h-5" />
                        素材中心
                    </h1>
                    <p className="text-sm text-zinc-500 mt-1">
                        Web3 热点素材 · AI 智能筛选 · 一键创作
                    </p>
                </div>

                <button
                    onClick={handleFetch}
                    disabled={fetching}
                    className={cn(
                        "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all",
                        fetching
                            ? "bg-zinc-100 text-zinc-400 cursor-wait"
                            : "bg-zinc-900 text-white hover:bg-zinc-700 shadow-sm hover:shadow-md"
                    )}
                >
                    {fetching ? (
                        <><Loader2 className="w-4 h-4 animate-spin" />抓取中...</>
                    ) : (
                        <><RefreshCw className="w-4 h-4" />抓取最新</>
                    )}
                </button>
            </div>

            {/* Stats Bar */}
            {stats && stats.total > 0 && (
                <div className="grid grid-cols-4 gap-3 mb-6">
                    <div className="bg-white rounded-xl border border-zinc-100 p-3 text-center">
                        <div className="text-2xl font-bold text-zinc-900">{stats.total}</div>
                        <div className="text-xs text-zinc-500">总素材</div>
                    </div>
                    <div className="bg-white rounded-xl border border-zinc-100 p-3 text-center">
                        <div className="text-2xl font-bold text-emerald-600">{stats.fresh_count}</div>
                        <div className="text-xs text-zinc-500">新鲜素材</div>
                    </div>
                    <div className="bg-white rounded-xl border border-zinc-100 p-3 text-center">
                        <div className="text-2xl font-bold text-amber-600">{stats.score_avg}</div>
                        <div className="text-xs text-zinc-500">平均评分</div>
                    </div>
                    <div className="bg-white rounded-xl border border-zinc-100 p-3 text-center">
                        <div className="text-2xl font-bold text-violet-600">
                            {stats.by_status?.['未使用'] || 0}
                        </div>
                        <div className="text-xs text-zinc-500">待使用</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="flex items-center gap-2 mb-4 flex-wrap">
                <Filter className="w-4 h-4 text-zinc-400" />

                <select
                    value={filter.content_type}
                    onChange={e => { setFilter(f => ({ ...f, content_type: e.target.value })); setPage(1); }}
                    className="px-3 py-1.5 rounded-lg border border-zinc-200 text-xs bg-white focus:ring-1 focus:ring-zinc-300 outline-none"
                >
                    <option value="">所有类型</option>
                    <option value="精选快讯">精选快讯</option>
                    <option value="快讯">快讯</option>
                    <option value="长文">长文</option>
                </select>

                <select
                    value={filter.min_score.toString()}
                    onChange={e => { setFilter(f => ({ ...f, min_score: parseInt(e.target.value) })); setPage(1); }}
                    className="px-3 py-1.5 rounded-lg border border-zinc-200 text-xs bg-white focus:ring-1 focus:ring-zinc-300 outline-none"
                >
                    <option value="0">所有评分</option>
                    <option value="5">≥5 分</option>
                    <option value="7">≥7 分</option>
                    <option value="8">≥8 分 (精选)</option>
                </select>

                <select
                    value={filter.timeliness}
                    onChange={e => { setFilter(f => ({ ...f, timeliness: e.target.value })); setPage(1); }}
                    className="px-3 py-1.5 rounded-lg border border-zinc-200 text-xs bg-white focus:ring-1 focus:ring-zinc-300 outline-none"
                >
                    <option value="">所有时效</option>
                    <option value="fresh">新鲜 (&lt;24h)</option>
                    <option value="recent">近期 (1-3天)</option>
                </select>

                <span className="text-xs text-zinc-400 ml-auto">
                    共 {total} 条
                </span>
            </div>

            {/* Material List */}
            {loading ? (
                <div className="flex flex-col items-center justify-center py-20 text-zinc-400 gap-3">
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span className="text-sm">加载中...</span>
                </div>
            ) : items.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-zinc-400 gap-3">
                    <Newspaper className="w-10 h-10 text-zinc-200" />
                    <p className="text-sm">还没有素材</p>
                    <p className="text-xs">点击「抓取最新」开始收集 Web3 热点</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {items.map((item, i) => (
                        <MaterialCard
                            key={item.fingerprint || i}
                            item={item}
                            onUseForCreation={handleUseForCreation}
                        />
                    ))}
                </div>
            )}

            {/* Pagination */}
            {pageCount > 1 && (
                <div className="flex items-center justify-center gap-2 mt-6">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-3 py-1.5 text-xs border border-zinc-200 rounded-lg hover:bg-zinc-50 disabled:opacity-40"
                    >
                        上一页
                    </button>
                    <span className="text-xs text-zinc-500">
                        {page} / {pageCount}
                    </span>
                    <button
                        onClick={() => setPage(p => Math.min(pageCount, p + 1))}
                        disabled={page === pageCount}
                        className="px-3 py-1.5 text-xs border border-zinc-200 rounded-lg hover:bg-zinc-50 disabled:opacity-40"
                    >
                        下一页
                    </button>
                </div>
            )}
        </div>
    );
}
