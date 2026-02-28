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
 * P31: 发布文案组件
 * 第一条是主推文（聚合速报），其余是各项目要点
 * 用户一键复制主推文 + 配图 → 发到 X
 */
export function TweetCards({ tweets }: TweetCardsProps) {
    const [copied, setCopied] = useState(false);
    const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

    if (!tweets.length) return null;

    // 第一条是主推文，其余是补充要点
    const mainTweet = tweets[0];
    const detailTweets = tweets.slice(1);

    const handleCopyMain = async () => {
        try {
            await navigator.clipboard.writeText(mainTweet.text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            const textarea = document.createElement('textarea');
            textarea.value = mainTweet.text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            {/* 区域头部 */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-100">
                <div className="flex items-center gap-2 text-sm font-medium text-ink-primary">
                    <MessageSquare size={16} />
                    发布文案
                </div>
                <button
                    onClick={handleCopyMain}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border border-zinc-200 hover:bg-zinc-50"
                >
                    {copied ? (
                        <><Check size={12} className="text-green-500" /> 已复制</>
                    ) : (
                        <><Copy size={12} /> 复制推文</>
                    )}
                </button>
            </div>

            <div className="px-5 py-4 space-y-3">
                {/* 使用提示 */}
                <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg text-[11px] text-blue-700">
                    <Send size={14} />
                    复制推文 + 配图 → 发布到 X
                </div>

                {/* 主推文 */}
                <div className="border border-zinc-200 rounded-lg p-4 bg-zinc-50/50">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-ink-primary px-2 py-0.5 bg-violet-100 text-violet-700 rounded">
                            主推文
                        </span>
                        <span className="text-[10px] text-ink-muted">
                            {mainTweet.char_count}字
                        </span>
                    </div>
                    <p className="text-sm text-ink-primary leading-relaxed whitespace-pre-line">
                        {mainTweet.text}
                    </p>
                </div>

                {/* 各项目详细要点（可折叠） */}
                {detailTweets.length > 0 && (
                    <div className="space-y-1.5">
                        <div className="text-[11px] text-ink-muted font-medium px-1">
                            📋 各项目要点 ({detailTweets.length})
                        </div>
                        {detailTweets.map((tweet, idx) => (
                            <div
                                key={idx}
                                className="group border border-zinc-100 rounded-lg px-3 py-2.5 hover:border-zinc-200 transition-colors cursor-pointer"
                                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                            >
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-medium text-ink-primary">{tweet.name}</span>
                                    <span className="text-[10px] text-ink-muted">
                                        {expandedIdx === idx ? '收起' : '展开'}
                                    </span>
                                </div>
                                {expandedIdx === idx && (
                                    <p className="text-xs text-ink-muted leading-relaxed whitespace-pre-line mt-1.5">
                                        {tweet.text}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
