'use client';

import { useState } from 'react';
import { Copy, Check, MessageSquare, Send, ChevronDown, ChevronUp } from 'lucide-react';

interface Tweet {
    name: string;
    text: string;
    char_count: number;
    twitter?: string;
}

interface TweetCardsProps {
    tweets: Tweet[];
}

/**
 * P32: 发布文案组件（增强版）
 * - 主推文：展开/收起 + 字符进度条
 * - 各项目要点：mini字符条 + 单项复制
 * - 复制始终复制全文，不受折叠状态影响
 */
export function TweetCards({ tweets }: TweetCardsProps) {
    const [copied, setCopied] = useState(false);
    const [expandedMain, setExpandedMain] = useState(false);
    const [expandedIdx, setExpandedIdx] = useState<number | null>(null);
    const [copiedDetail, setCopiedDetail] = useState<number | null>(null);

    if (!tweets.length) return null;

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

    const handleCopyDetail = async (idx: number, text: string) => {
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
        setCopiedDetail(idx);
        setTimeout(() => setCopiedDetail(null), 2000);
    };

    // 主推文行数估算（约每行40字）
    const mainLines = mainTweet.text.split('\n');
    const showExpandBtn = mainLines.length > 4 || mainTweet.text.length > 160;

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

                {/* 主推文（可展开/收起）*/}
                <div className="border border-zinc-200 rounded-lg p-4 bg-zinc-50/50">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold px-2 py-0.5 bg-violet-100 text-violet-700 rounded">
                            主推文
                        </span>
                        <span className="text-[10px] text-ink-muted">
                            {mainTweet.char_count}字
                        </span>
                    </div>

                    {/* 文本区（折叠/展开）*/}
                    <div className="relative">
                        <p
                            className="text-sm text-ink-primary leading-relaxed whitespace-pre-line transition-all duration-200"
                            style={
                                !expandedMain && showExpandBtn
                                    ? { maxHeight: '6.5em', overflow: 'hidden' }
                                    : expandedMain
                                        ? { maxHeight: '400px', overflowY: 'auto' }
                                        : undefined
                            }
                        >
                            {mainTweet.text}
                        </p>
                        {/* 渐变遮罩 */}
                        {!expandedMain && showExpandBtn && (
                            <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-zinc-50 to-transparent pointer-events-none" />
                        )}
                    </div>

                    {/* 展开/收起按钮 */}
                    {showExpandBtn && (
                        <button
                            onClick={() => setExpandedMain(!expandedMain)}
                            className="flex items-center gap-1 mt-1 text-[11px] text-violet-600 hover:text-violet-800 font-medium transition-colors"
                        >
                            {expandedMain ? (
                                <><ChevronUp size={14} /> 收起</>
                            ) : (
                                <><ChevronDown size={14} /> 展开全文</>
                            )}
                        </button>
                    )}

                    {/* P32: 字符进度条 */}
                    <CharBar charCount={mainTweet.char_count} />
                </div>

                {/* 各项目详细要点（带 mini 字符条 + 单项复制）*/}
                {detailTweets.length > 0 && (
                    <div className="space-y-1.5">
                        <div className="text-[11px] text-ink-muted font-medium px-1">
                            📋 各项目要点 ({detailTweets.length})
                        </div>
                        {detailTweets.map((tweet, idx) => (
                            <div
                                key={idx}
                                className="group border border-zinc-100 rounded-lg px-3 py-2.5 hover:border-zinc-200 transition-colors"
                            >
                                <div
                                    className="flex items-center gap-2 cursor-pointer"
                                    onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                                >
                                    <span className="text-xs font-medium text-ink-primary">
                                        {tweet.name}
                                    </span>
                                    {/* mini 字符条 */}
                                    <MiniCharBar charCount={tweet.char_count} />
                                    <span className="text-[10px] text-ink-muted ml-auto">
                                        {expandedIdx === idx ? '收起' : '展开'}
                                    </span>
                                </div>
                                {expandedIdx === idx && (
                                    <div className="mt-1.5 pt-1.5 border-t border-zinc-100">
                                        <p className="text-xs text-ink-muted leading-relaxed whitespace-pre-line">
                                            {tweet.text}
                                        </p>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleCopyDetail(idx, tweet.text);
                                            }}
                                            className="mt-2 flex items-center gap-1 px-2 py-1 text-[10px] font-medium text-zinc-500 hover:text-zinc-700 border border-zinc-200 rounded-md hover:bg-zinc-50 transition-colors"
                                        >
                                            {copiedDetail === idx ? (
                                                <><Check size={10} className="text-green-500" /> 已复制</>
                                            ) : (
                                                <><Copy size={10} /> 复制此项</>
                                            )}
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

/** P32: 主推文字符进度条 */
function CharBar({ charCount }: { charCount: number }) {
    const limit = 280;
    const pct = Math.min((charCount / limit) * 100, 100);
    const isOver = charCount > limit;

    return (
        <div className="flex items-center gap-2 mt-2 pt-2 border-t border-zinc-100">
            <span className="text-[10px] text-ink-muted">字数</span>
            <div className="flex-1 h-1 bg-zinc-100 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-300 ${isOver ? 'bg-red-500' : pct > 80 ? 'bg-amber-400' : 'bg-emerald-400'
                        }`}
                    style={{ width: `${pct}%` }}
                />
            </div>
            <span
                className={`text-[10px] tabular-nums ${isOver ? 'text-red-600 font-semibold' : 'text-ink-muted'
                    }`}
            >
                {charCount} / {limit}
                {isOver && ` ⚠️ 超${charCount - limit}字`}
            </span>
        </div>
    );
}

/** P32: 项目要点 mini 字符条 */
function MiniCharBar({ charCount }: { charCount: number }) {
    const limit = 280;
    const pct = Math.min((charCount / limit) * 100, 100);
    const isOver = charCount > limit;

    return (
        <div className="flex items-center gap-1.5 ml-1">
            <div className="w-10 h-[3px] bg-zinc-100 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full ${isOver ? 'bg-red-500' : 'bg-emerald-400'
                        }`}
                    style={{ width: `${pct}%` }}
                />
            </div>
            <span className="text-[9px] text-ink-muted tabular-nums">{charCount}字</span>
        </div>
    );
}
