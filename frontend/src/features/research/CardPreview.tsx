'use client';

import { useRef, useState } from 'react';
import { Copy, Check, Image } from 'lucide-react';

interface CardPreviewProps {
    html: string;
    date: string;
}

const CARD_W = 1200;
const CARD_H = 675;

/**
 * P32: 配图预览组件（全宽版）
 * 配图占满主内容区，完整显示所有项目卡片
 */
export function CardPreview({ html, date }: CardPreviewProps) {
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const [copied, setCopied] = useState(false);
    const [copying, setCopying] = useState(false);

    const handleCopyImage = async () => {
        if (copying) return;
        setCopying(true);
        try {
            const offscreen = document.createElement('div');
            offscreen.style.cssText = `position:fixed;left:-9999px;top:0;width:${CARD_W}px;height:${CARD_H}px;overflow:hidden;z-index:-1;`;

            const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
            const styleMatch = html.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
            const bodyContent = bodyMatch ? bodyMatch[1] : '';
            const styleContent = styleMatch ? styleMatch[1] : '';

            // 直接插入 DOM（不用 Shadow DOM，确保 html2canvas 能访问字体）
            const styleEl = document.createElement('style');
            styleEl.textContent = styleContent;
            offscreen.appendChild(styleEl);
            offscreen.insertAdjacentHTML('beforeend', bodyContent);
            document.body.appendChild(offscreen);

            // 预加载 Google Font 并等待渲染
            try {
                await document.fonts.load('900 42px Inter');
                await document.fonts.load('400 14px Inter');
            } catch { }
            await new Promise(r => setTimeout(r, 200));

            const html2canvas = (await import('html2canvas')).default;
            const canvas = await html2canvas(offscreen.querySelector('.canvas') as HTMLElement || offscreen, {
                backgroundColor: '#050505',
                scale: 4,
                useCORS: true,
                width: CARD_W,
                height: CARD_H,
            });

            document.body.removeChild(offscreen);

            canvas.toBlob(async (blob) => {
                if (blob) {
                    try {
                        await navigator.clipboard.write([
                            new ClipboardItem({ 'image/png': blob })
                        ]);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                    } catch {
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `research_${date}.png`;
                        a.click();
                        URL.revokeObjectURL(url);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                    }
                }
            }, 'image/png');
        } catch (err) {
            console.error('截图失败:', err);
        } finally {
            setCopying(false);
        }
    };

    return (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            {/* 区域头部 */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-100">
                <div className="flex items-center gap-2 text-sm font-medium text-ink-primary">
                    <Image size={16} />
                    配图预览
                </div>
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

            {/* 配图渲染 — 全宽 iframe */}
            <div className="bg-[#050505] w-full" style={{ aspectRatio: `${CARD_W}/${CARD_H}` }}>
                <iframe
                    ref={iframeRef}
                    srcDoc={html}
                    title="投研配图预览"
                    sandbox="allow-same-origin"
                    scrolling="no"
                    className="w-full h-full border-0 block"
                    style={{ overflow: 'hidden' }}
                />
            </div>
        </div>
    );
}
