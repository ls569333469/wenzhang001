'use client';

import { useState } from 'react';
import { Copy, Check, Image, Download } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

interface CardPreviewProps {
    html: string;
    date: string;
    cardImageUrl?: string | null;
}

const CARD_W = 1200;
const CARD_H = 675;

/**
 * P33: 配图预览组件
 * - 有 PNG 时显示 <img>（可右键复制）
 * - 无 PNG 时 fallback 到 iframe 预览
 * - "复制图片"按钮从后端获取预渲染 PNG → 剪贴板
 */
export function CardPreview({ html, date, cardImageUrl }: CardPreviewProps) {
    const [copied, setCopied] = useState(false);
    const [copying, setCopying] = useState(false);

    // 完整后端 URL
    const fullImageUrl = cardImageUrl ? `${API_BASE_URL}${cardImageUrl}` : null;
    const dateRaw = date.replace(/-/g, '');

    const handleCopyImage = async () => {
        if (copying) return;
        setCopying(true);
        try {
            // 确定图片 URL
            let imgUrl = fullImageUrl;
            if (!imgUrl) {
                // 触发后端生成
                const res = await fetch(`${API_BASE_URL}/api/research/regen-card-image/${dateRaw}`, { method: 'POST' });
                if (!res.ok) throw new Error('生成配图失败');
                imgUrl = `${API_BASE_URL}/api/research/card-image/${dateRaw}`;
            }

            // 获取 PNG blob
            const imgRes = await fetch(imgUrl);
            if (!imgRes.ok) throw new Error('获取图片失败');
            const blob = await imgRes.blob();

            // 尝试复制到剪贴板
            try {
                await navigator.clipboard.write([
                    new ClipboardItem({ 'image/png': blob })
                ]);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            } catch {
                // 剪贴板不可用 → 下载
                downloadBlob(blob);
            }
        } catch (err) {
            console.error('复制图片失败:', err);
        } finally {
            setCopying(false);
        }
    };

    const handleDownload = async () => {
        try {
            const imgUrl = fullImageUrl || `${API_BASE_URL}/api/research/card-image/${dateRaw}`;
            const res = await fetch(imgUrl);
            if (!res.ok) throw new Error('获取图片失败');
            downloadBlob(await res.blob());
        } catch (err) {
            console.error('下载失败:', err);
        }
    };

    const downloadBlob = (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `alpha_daily_${date}.png`;
        a.click();
        URL.revokeObjectURL(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            {/* 区域头部 */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-100">
                <div className="flex items-center gap-2 text-sm font-medium text-ink-primary">
                    <Image size={16} />
                    配图预览
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleDownload}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border border-zinc-200 hover:bg-zinc-50"
                    >
                        <Download size={12} /> 下载图片
                    </button>
                    <button
                        onClick={handleCopyImage}
                        disabled={copying}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border border-zinc-200 hover:bg-zinc-50 disabled:opacity-50"
                    >
                        {copied ? (
                            <><Check size={12} className="text-green-500" /> 已复制</>
                        ) : copying ? (
                            <><span className="animate-spin">⏳</span> 截图中...</>
                        ) : (
                            <><Copy size={12} /> 复制图片</>
                        )}
                    </button>
                </div>
            </div>

            {/* 配图渲染 */}
            <div className="bg-[#F4F3EE] w-full" style={{ aspectRatio: `${CARD_W}/${CARD_H}` }}>
                {fullImageUrl ? (
                    /* 方案B: 直接显示后端 PNG，用户可右键复制 */
                    <img
                        src={fullImageUrl}
                        alt="投研配图"
                        className="w-full h-full object-contain"
                        draggable
                    />
                ) : (
                    /* fallback: iframe 预览 */
                    <iframe
                        srcDoc={html}
                        title="投研配图预览"
                        sandbox="allow-same-origin"
                        scrolling="no"
                        className="w-full h-full border-0 block"
                        style={{ overflow: 'hidden' }}
                    />
                )}
            </div>
        </div>
    );
}
