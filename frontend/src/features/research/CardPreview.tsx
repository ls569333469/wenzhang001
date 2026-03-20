'use client';

import { useState, useRef, useCallback } from 'react';
import { Copy, Check, Image, Download } from 'lucide-react';
import html2canvas from 'html2canvas';
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
 * 
 * 复制/下载方案（借鉴 project.zip 的 canvas 导出思路）：
 * - 有 PNG 时：fetch → Object URL → Canvas → Blob
 * - 无 PNG 时：将 card HTML 渲染到隐藏 div → html2canvas 截图 → Blob
 */
export function CardPreview({ html, date, cardImageUrl }: CardPreviewProps) {
    const [copied, setCopied] = useState(false);
    const [copying, setCopying] = useState(false);
    const offscreenRef = useRef<HTMLDivElement>(null);

    const fullImageUrl = cardImageUrl ? `${API_BASE_URL}${cardImageUrl}` : null;
    const dateRaw = date.replace(/-/g, '');

    /**
     * 方案 A：后端已有 PNG → 直接 fetch 原始字节（不经过 Canvas，避免重渲染偏移）
     */
    const getBlobFromPng = async (): Promise<Blob> => {
        const imgUrl = fullImageUrl!;
        const response = await fetch(imgUrl);
        if (!response.ok) throw new Error('PNG 404');
        const fetchedBlob = await response.blob();
        // 确保 MIME 类型为 image/png（剪贴板 API 要求精确匹配）
        return fetchedBlob.type === 'image/png'
            ? fetchedBlob
            : new Blob([fetchedBlob], { type: 'image/png' });
    };

    /**
     * 方案 B：仅有 HTML（PNG 不存在）→ 渲染到隐藏 div → html2canvas 截图
     * 注意：不能用 iframe（html2canvas 无法捕获 iframe 内容），
     * 所以提取 card HTML 中 <body> 的内容 + <style> 渲染到真实 div。
     */
    const getBlobFromHtml = async (): Promise<Blob> => {
        // 创建一个隐藏的渲染容器
        const container = document.createElement('div');
        container.style.cssText = `
            position: fixed; left: -9999px; top: 0;
            width: ${CARD_W}px; height: ${CARD_H}px;
            overflow: hidden; z-index: -1;
        `;

        // 提取 card HTML 中的 style 和 body 内容
        const styleMatch = html.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
        const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);

        if (styleMatch) {
            const style = document.createElement('style');
            style.textContent = styleMatch[1];
            container.appendChild(style);
        }
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = bodyMatch ? bodyMatch[1] : html;
        container.appendChild(contentDiv);
        document.body.appendChild(container);

        try {
            // 等待字体加载
            await document.fonts.ready;
            await new Promise(r => setTimeout(r, 300));

            // html2canvas 截取（与 project.zip 的 getDataURL 等价）
            const canvas = await html2canvas(container, {
                width: CARD_W,
                height: CARD_H,
                scale: 2,
                backgroundColor: '#F4F3EE',
                useCORS: true,
                logging: false,
            });

            return new Promise<Blob>((resolve, reject) => {
                canvas.toBlob(b => b ? resolve(b) : reject(new Error('toBlob failed')), 'image/png');
            });
        } finally {
            document.body.removeChild(container);
        }
    };

    /**
     * 获取卡片 Blob：优先用 PNG，降级用 HTML 渲染
     */
    const getCardBlob = useCallback(async (): Promise<Blob> => {
        // 优先用后端 PNG
        if (fullImageUrl) {
            try {
                return await getBlobFromPng();
            } catch {
                // PNG 失败，降级到 HTML 渲染
            }
        }
        return await getBlobFromHtml();
    }, [fullImageUrl, html, dateRaw]);

    const handleCopyImage = async () => {
        if (copying) return;
        setCopying(true);
        try {
            const blob = await getCardBlob();
            await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': blob })
            ]);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('复制图片失败:', err);
            // Fallback: 下载
            try {
                const blob = await getCardBlob();
                downloadBlob(blob);
            } catch {}
        } finally {
            setCopying(false);
        }
    };

    const handleDownload = async () => {
        setCopying(true);
        try {
            const blob = await getCardBlob();
            downloadBlob(blob);
        } catch (err) {
            console.error('下载失败:', err);
        } finally {
            setCopying(false);
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
                        disabled={copying}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border border-zinc-200 hover:bg-zinc-50 disabled:opacity-50"
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
                    <img src={fullImageUrl} alt="投研配图" className="w-full h-full object-contain" draggable />
                ) : (
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
