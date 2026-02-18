'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Copy, Trash2, Check, FileText, Clock, Star } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { API_BASE_URL } from '@/config/api';
import { marked } from 'marked';

interface CreationItem {
    id: string;
    title: string;
    mode: string;
    input_topic: string;
    critic_score: number;
    critic_verdict: string;
    word_count: number;
    created_at: string;
    preview?: string;
    content?: string;
}

const MODE_LABELS: Record<string, string> = {
    short_article: '短文',
    mid_article: '中篇',
    long_article: '长篇',
    hot_take: '锐评',
    tutorial: '教程',
    rewrite: '改写',
    unknown: '未知',
};

export function CreationHistory() {
    const router = useRouter();
    const [items, setItems] = useState<CreationItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const [expandedContent, setExpandedContent] = useState<string>('');
    const [loadingContent, setLoadingContent] = useState(false);
    const [copied, setCopied] = useState<string | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

    // Load list
    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                const params = new URLSearchParams({ page: page.toString(), page_size: '20' });
                const resp = await fetch(`${API_BASE_URL}/creations/list?${params}`);
                if (!resp.ok) throw new Error('Failed to load');
                const data = await resp.json();
                setItems(data.items || []);
                setTotal(data.total || 0);
            } catch (err) {
                console.error('Load creations error:', err);
                toast.error('加载创作历史失败');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [page]);

    // Expand item
    const handleExpand = async (id: string) => {
        if (expandedId === id) {
            setExpandedId(null);
            return;
        }
        setExpandedId(id);
        setLoadingContent(true);
        try {
            const resp = await fetch(`${API_BASE_URL}/creations/${id}`);
            if (!resp.ok) throw new Error('Failed to load');
            const data = await resp.json();
            setExpandedContent(data.content || '');
        } catch {
            toast.error('加载内容失败');
        } finally {
            setLoadingContent(false);
        }
    };

    // Copy content
    const handleCopy = async (id: string) => {
        if (!expandedContent) return;
        await navigator.clipboard.writeText(expandedContent);
        setCopied(id);
        toast.success('已复制到剪贴板');
        setTimeout(() => setCopied(null), 2000);
    };

    // Delete
    const handleDelete = async (id: string) => {
        try {
            const resp = await fetch(`${API_BASE_URL}/creations/${id}`, { method: 'DELETE' });
            if (!resp.ok) throw new Error('Delete failed');
            setItems(items.filter(i => i.id !== id));
            setTotal(t => t - 1);
            setDeleteConfirm(null);
            if (expandedId === id) setExpandedId(null);
            toast.success('已删除');
        } catch {
            toast.error('删除失败');
        }
    };

    const formatDate = (iso: string) => {
        try {
            const d = new Date(iso);
            return `${d.getMonth() + 1}月${d.getDate()}日 ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
        } catch {
            return iso;
        }
    };

    const totalPages = Math.ceil(total / 20);

    return (
        <div className="w-full max-w-[960px] mx-auto py-8 px-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => router.push('/studio')}
                        className="flex items-center gap-1.5 px-3 py-2 text-sm text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 rounded-lg transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        返回工作台
                    </button>
                    <div>
                        <h1 className="text-xl font-bold text-zinc-900">创作历史</h1>
                        <p className="text-sm text-zinc-500 mt-0.5">共 {total} 篇保存的创作</p>
                    </div>
                </div>
            </div>

            {/* List */}
            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-400"></div>
                </div>
            ) : items.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-zinc-400">
                    <FileText className="w-12 h-12 mb-4 opacity-50" />
                    <p className="text-lg font-medium">暂无保存的创作</p>
                    <p className="text-sm mt-1">生成内容后点击「保存」按钮即可在此查看</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {items.map((item) => (
                        <div key={item.id} className="group">
                            {/* Card */}
                            <div
                                onClick={() => handleExpand(item.id)}
                                className={cn(
                                    "bg-white border rounded-xl p-4 cursor-pointer transition-all duration-200 hover:shadow-md",
                                    expandedId === item.id
                                        ? "border-blue-300 shadow-md ring-1 ring-blue-100"
                                        : "border-zinc-200 hover:border-zinc-300"
                                )}
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-semibold text-zinc-900 truncate">{item.title}</h3>
                                        <p className="text-sm text-zinc-500 mt-1 line-clamp-2">{item.preview}</p>
                                        <div className="flex items-center gap-3 mt-3">
                                            <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-zinc-100 text-zinc-600 rounded-full">
                                                {MODE_LABELS[item.mode] || item.mode}
                                            </span>
                                            {item.critic_score > 0 && (
                                                <span className="inline-flex items-center gap-1 text-xs text-amber-600">
                                                    <Star className="w-3 h-3" />
                                                    {item.critic_score}分
                                                </span>
                                            )}
                                            {item.word_count > 0 && (
                                                <span className="text-xs text-zinc-400">{item.word_count}字</span>
                                            )}
                                            <span className="inline-flex items-center gap-1 text-xs text-zinc-400">
                                                <Clock className="w-3 h-3" />
                                                {formatDate(item.created_at)}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        {deleteConfirm === item.id ? (
                                            <>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                                                    className="px-2 py-1 text-xs text-red-600 bg-red-50 hover:bg-red-100 rounded transition-colors"
                                                >
                                                    确认
                                                </button>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); setDeleteConfirm(null); }}
                                                    className="px-2 py-1 text-xs text-zinc-500 hover:bg-zinc-100 rounded transition-colors"
                                                >
                                                    取消
                                                </button>
                                            </>
                                        ) : (
                                            <button
                                                onClick={(e) => { e.stopPropagation(); setDeleteConfirm(item.id); }}
                                                className="p-1.5 text-zinc-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                                title="删除"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Expanded Content */}
                            {expandedId === item.id && (
                                <div className="mt-2 bg-white border border-blue-200 rounded-xl p-6 animate-in slide-in-from-top-2 duration-200">
                                    {loadingContent ? (
                                        <div className="flex items-center justify-center py-8">
                                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex justify-end mb-4">
                                                <button
                                                    onClick={() => handleCopy(item.id)}
                                                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-600 bg-zinc-50 hover:bg-zinc-100 rounded-lg border border-zinc-200 transition-colors"
                                                >
                                                    {copied === item.id ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                                    {copied === item.id ? '已复制' : '复制内容'}
                                                </button>
                                            </div>
                                            <div
                                                className="prose prose-zinc prose-sm max-w-none"
                                                dangerouslySetInnerHTML={{ __html: marked.parse(expandedContent) as string }}
                                            />
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-8">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 rounded-lg disabled:opacity-40 transition-colors"
                    >
                        上一页
                    </button>
                    <span className="text-sm text-zinc-500">
                        {page} / {totalPages}
                    </span>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 rounded-lg disabled:opacity-40 transition-colors"
                    >
                        下一页
                    </button>
                </div>
            )}
        </div>
    );
}
