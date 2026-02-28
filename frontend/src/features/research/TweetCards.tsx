'use client';

import { useState } from 'react';
import { Copy, Check, MessageSquare, Send } from 'lucide-react';

interface Tweet {
    name: string;
    text: string;
    char_count: number;
}

interface TweetCardsProps {
    tweets: Tweet[];
}

/**
 * P31: 推文文案组件
 * 合并所有项目推文为一条完整发布文案
 * 用户复制后直接粘贴到 X 发布
 */
export function TweetCards({ tweets }: TweetCardsProps) {
    const [copied, setCopied] = useState(false);
    const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

    // 合成一条完整发布文案
    const combinedText = tweets.map(t => t.text).join('\n\n---\n\n');
    const totalChars = combinedText.length;

    const handleCopyAll = async () => {
        try {
            await navigator.clipboard.writeText(combinedText);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            const textarea = document.createElement('textarea');
            textarea.value = combinedText;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleCopySingle = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
        } catch {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    };

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            {/* 区域头部 */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-100">
                <div className="flex items-center gap-2 text-sm font-medium text-ink-primary">
                    <MessageSquare size={16} />
                    发布文案
                    <span className="text-[10px] px-1.5 py-0.5 bg-zinc-100 text-ink-muted rounded-full">
                        {totalChars}字 · {tweets.length}个项目
                    </span>
                </div>
                <button
                    onClick={handleCopyAll}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border border-zinc-200 hover:bg-zinc-50"
                >
                    {copied ? (
                        <><Check size={12} className="text-green-500" /> 已复制全文</>
                    ) : (
                        <><Copy size={12} /> 复制全文</>
                    )}
                </button>
            </div>

            {/* 合成文案预览 */}
            <div className="px-5 py-4 space-y-3">
                {/* 使用提示 */}
                <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg text-[11px] text-blue-700">
                    <Send size={14} />
                    复制全文 + 配图 → 发布到 X
                </div>

                {/* 各项目文案 */}
                {tweets.map((tweet, idx) => (
                    <div
                        key={idx}
                        className="group border border-zinc-100 rounded-lg p-3 hover:border-zinc-200 transition-colors cursor-pointer"
                        onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                    >
                        <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-ink-primary">{tweet.name}</span>
                                <span className="text-[10px] px-1.5 py-0.5 bg-zinc-100 text-ink-muted rounded-full">
                                    {tweet.char_count}字
                                </span>
                            </div>
                            <button
                                onClick={(e) => { e.stopPropagation(); handleCopySingle(tweet.text); }}
                                className="opacity-0 group-hover:opacity-100 text-[10px] text-ink-muted hover:text-ink-primary transition-all"
                            >
                                复制单条
                            </button>
                        </div>
                        <p className={`text-xs text-ink-muted leading-relaxed whitespace-pre-line ${expandedIdx === idx ? '' : 'line-clamp-2'}`}>
                            {tweet.text}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
