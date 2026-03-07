'use client';

import { MessageCircle, Repeat2, Heart, BarChart3, Share } from 'lucide-react';

interface XPreviewProps {
    tweetText: string;
    cardHtml: string | null;
}

// P32: 硬编码账号信息，后续 Phase C 再改配置化
const X_ACCOUNT = {
    displayName: '雪球88',
    handle: '@xueqiu88',
    avatarText: '雪',
};

const PREVIEW_TEXT_MAX = 200;

/**
 * P32: X (Twitter) 发布预览组件（全宽版）
 * 模拟推文发出后在 X 时间线上的真实效果
 * 全宽布局，配图以 16:9 完整显示
 */
export function XPreview({ tweetText, cardHtml }: XPreviewProps) {
    const truncatedText =
        tweetText.length > PREVIEW_TEXT_MAX
            ? tweetText.slice(0, PREVIEW_TEXT_MAX) + '…'
            : tweetText;

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            {/* 区域头部 */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-100">
                <div className="flex items-center gap-2 text-sm font-medium text-ink-primary">
                    📱 发出后效果预览
                </div>
                <span className="text-[10px] text-ink-muted">仅供参考</span>
            </div>

            {/* X 风格推文卡片 */}
            <div className="px-5 py-4">
                <div className="border border-zinc-200 rounded-2xl p-4 bg-white max-w-[550px]">
                    {/* 头部：头像 + 名称 */}
                    <div className="flex items-start gap-3 mb-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                            {X_ACCOUNT.avatarText}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1.5">
                                <span className="text-[14px] font-bold text-zinc-900">
                                    {X_ACCOUNT.displayName}
                                </span>
                                <span className="text-[13px] text-zinc-500">
                                    {X_ACCOUNT.handle}
                                </span>
                            </div>

                            {/* 推文内容 */}
                            <div className="text-[14px] text-zinc-900 leading-relaxed whitespace-pre-line mt-1">
                                {truncatedText}
                            </div>

                            {/* 配图缩略 */}
                            {cardHtml && (
                                <div
                                    className="rounded-xl overflow-hidden border border-zinc-200 bg-[#050505] mt-3"
                                    style={{ aspectRatio: '1200/675' }}
                                >
                                    <iframe
                                        srcDoc={cardHtml}
                                        title="配图缩略预览"
                                        sandbox="allow-same-origin"
                                        scrolling="no"
                                        className="w-full h-full border-0 block"
                                        style={{ overflow: 'hidden', pointerEvents: 'none' }}
                                    />
                                </div>
                            )}

                            {/* 操作栏 */}
                            <div className="flex items-center gap-8 mt-3 pt-3 border-t border-zinc-100">
                                <XAction icon={<MessageCircle size={16} />} count="0" />
                                <XAction icon={<Repeat2 size={16} />} count="0" />
                                <XAction icon={<Heart size={16} />} count="0" />
                                <XAction icon={<BarChart3 size={16} />} count="0" />
                                <XAction icon={<Share size={16} />} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function XAction({ icon, count }: { icon: React.ReactNode; count?: string }) {
    return (
        <button className="flex items-center gap-1.5 text-zinc-400 hover:text-blue-500 transition-colors">
            {icon}
            {count && <span className="text-[12px]">{count}</span>}
        </button>
    );
}
