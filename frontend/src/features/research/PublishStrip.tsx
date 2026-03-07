'use client';

import { CheckCircle2, AlertTriangle, XCircle, Calendar, FileText } from 'lucide-react';

interface PublishStripProps {
    cardReady: boolean;
    mainTweetReady: boolean;
    mainTweetCharCount: number;
    projectCount: number;
    totalCharCount: number;
    date: string;
}

/**
 * P32: 发布检查清单条
 * 显示配图/主推文/字数/项目数状态，一眼确认发布就绪
 */
export function PublishStrip({
    cardReady,
    mainTweetReady,
    mainTweetCharCount,
    projectCount,
    totalCharCount,
    date,
}: PublishStripProps) {
    return (
        <div className="flex items-center gap-1.5 px-3 py-2 bg-white border border-zinc-200 rounded-xl flex-wrap">
            {/* 检查项 */}
            <CheckItem ok={cardReady} label="配图就绪" />
            <CheckItem ok={mainTweetReady} label="主推文" />
            <CheckItem
                ok={mainTweetCharCount <= 280}
                label={`字数 ${mainTweetCharCount}`}
                warn={mainTweetCharCount > 280}
            />
            <CheckItem ok={projectCount > 0} label={`${projectCount} 项目`} />

            {/* 分隔线 */}
            <div className="w-px h-4 bg-zinc-200 mx-1" />

            {/* 统计 */}
            <div className="flex items-center gap-1 text-[11px] text-ink-muted ml-auto">
                <Calendar size={12} />
                <span className="font-semibold text-ink-primary">{date}</span>
            </div>
            <div className="flex items-center gap-1 text-[11px] text-ink-muted">
                <FileText size={12} />
                <span className="font-semibold text-ink-primary">{totalCharCount.toLocaleString()}</span>
                <span>总字</span>
            </div>
        </div>
    );
}

function CheckItem({ ok, label, warn }: { ok: boolean; label: string; warn?: boolean }) {
    const isWarn = warn && !ok;
    return (
        <div
            className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium ${ok
                    ? 'bg-emerald-50 text-emerald-700'
                    : isWarn
                        ? 'bg-amber-50 text-amber-700'
                        : 'bg-red-50 text-red-600'
                }`}
        >
            {ok ? (
                <CheckCircle2 size={12} />
            ) : isWarn ? (
                <AlertTriangle size={12} />
            ) : (
                <XCircle size={12} />
            )}
            {label}
        </div>
    );
}
