'use client';

import { useRef, useState } from 'react';
import { Copy, Check, Image } from 'lucide-react';

interface CardPreviewProps {
    html: string;
    date: string;
}

export function CardPreview({ html, date }: CardPreviewProps) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [copied, setCopied] = useState(false);
    const [copying, setCopying] = useState(false);

    const handleCopyImage = async () => {
        if (!cardRef.current || copying) return;
        setCopying(true);
        try {
            // 动态导入 html2canvas
            const html2canvas = (await import('html2canvas')).default;
            const canvas = await html2canvas(cardRef.current, {
                backgroundColor: '#050505',
                scale: 2,
                useCORS: true,
                width: 1200,
                height: 675,
            });
            canvas.toBlob(async (blob) => {
                if (blob) {
                    try {
                        await navigator.clipboard.write([
                            new ClipboardItem({ 'image/png': blob })
                        ]);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                    } catch {
                        // Fallback: 下载图片
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

    // 从完整 HTML 中提取 body 内容
    const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    const styleMatch = html.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
    const bodyContent = bodyMatch ? bodyMatch[1] : '';
    const styleContent = styleMatch ? styleMatch[1] : '';

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

            {/* 配图渲染区域 */}
            <div className="bg-[#050505] flex justify-center p-6 overflow-auto">
                <div
                    ref={cardRef}
                    style={{ width: 1200, height: 675, transform: 'scale(0.85)', transformOrigin: 'top center' }}
                >
                    <style dangerouslySetInnerHTML={{ __html: styleContent }} />
                    <div dangerouslySetInnerHTML={{ __html: bodyContent }} />
                </div>
            </div>
        </div>
    );
}
