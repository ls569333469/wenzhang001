'use client';

import { useState } from 'react';
import { Copy, Check, MessageSquare } from 'lucide-react';

interface Tweet {
    name: string;
    text: string;
    char_count: number;
}

interface TweetCardsProps {
    tweets: Tweet[];
}

export function TweetCards({ tweets }: TweetCardsProps) {
    const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

    const handleCopy = async (text: string, idx: number) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedIdx(idx);
            setTimeout(() => setCopiedIdx(null), 2000);
        } catch {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            setCopiedIdx(idx);
            setTimeout(() => setCopiedIdx(null), 2000);
        }
    };

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            {/* 区域头部 */}
            <div className="flex items-center gap-2 px-5 py-3 border-b border-zinc-100 text-sm font-medium text-ink-primary">
                <MessageSquare size={16} />
                推文文案
                <span className="text-ink-muted font-normal">({tweets.length})</span>
            </div>

            {/* 推文列表 */}
            <div className="divide-y divide-zinc-100">
                {tweets.map((tweet, idx) => (
                    <div key={idx} className="flex items-start gap-4 px-5 py-4 hover:bg-zinc-50/50 transition-colors">
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1.5">
                                <span className="text-sm font-medium text-ink-primary">{tweet.name}</span>
                                <span className="text-[10px] px-1.5 py-0.5 bg-zinc-100 text-ink-muted rounded-full">
                                    {tweet.char_count}字
                                </span>
                            </div>
                            <p className="text-xs text-ink-muted leading-relaxed line-clamp-3 whitespace-pre-line">
                                {tweet.text}
                            </p>
                        </div>
                        <button
                            onClick={() => handleCopy(tweet.text, idx)}
                            className="shrink-0 flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-zinc-200 hover:bg-zinc-50 transition-colors"
                        >
                            {copiedIdx === idx ? (
                                <><Check size={12} className="text-green-500" /> 已复制</>
                            ) : (
                                <><Copy size={12} /> 复制</>
                            )}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
