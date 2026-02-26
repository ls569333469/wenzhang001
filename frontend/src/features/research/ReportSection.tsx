'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ReportSectionProps {
    markdown: string;
}

export function ReportSection({ markdown }: ReportSectionProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(markdown);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            const textarea = document.createElement('textarea');
            textarea.value = markdown;
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
            {/* 折叠头部 */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between px-5 py-3 hover:bg-zinc-50 transition-colors"
            >
                <div className="flex items-center gap-2 text-sm font-medium text-ink-primary">
                    <FileText size={16} />
                    完整报告
                    <span className="text-ink-muted font-normal text-xs">
                        (推 TG 用)
                    </span>
                </div>
                {isExpanded ? <ChevronUp size={16} className="text-ink-muted" /> : <ChevronDown size={16} className="text-ink-muted" />}
            </button>

            {/* 展开内容 */}
            {isExpanded && (
                <div className="border-t border-zinc-100">
                    <div className="flex justify-end px-5 py-2 border-b border-zinc-50">
                        <button
                            onClick={handleCopy}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-zinc-200 hover:bg-zinc-50 transition-colors"
                        >
                            {copied ? (
                                <><Check size={12} className="text-green-500" /> 已复制</>
                            ) : (
                                <><Copy size={12} /> 复制全文</>
                            )}
                        </button>
                    </div>
                    <div className="px-8 py-6 prose prose-zinc prose-sm max-w-none
                        prose-headings:font-serif prose-h1:text-lg prose-h2:text-base
                        prose-p:text-ink-muted prose-p:leading-relaxed
                        prose-table:text-xs prose-th:bg-zinc-50 prose-th:py-2
                    ">
                        <ReactMarkdown>{markdown}</ReactMarkdown>
                    </div>
                </div>
            )}
        </div>
    );
}
