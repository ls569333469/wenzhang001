'use client'

import { Button } from "@/components/ui/button"
import { ArrowRight, Brain, PenTool, StopCircle, Copy, Save } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'
import { toast } from "sonner"
import { useWorkbenchStore } from "../stores/useWorkbenchStore"
import { useGeneration } from "../hooks/useGeneration"

export function WritingCanvas() {
    const { stage, loading, options, result, setStage, setOptions, setResult } = useWorkbenchStore()
    const { handleAnalyze, handleGenerate, handleStop } = useGeneration()

    // Handlers
    const handleCopy = async () => {
        if (!result) return
        try {
            await navigator.clipboard.writeText(result)
            toast.success("Copied to clipboard")
        } catch (err) {
            toast.error("Failed to copy")
        }
    }

    const handleExport = () => {
        if (!result) return
        const blob = new Blob([result], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `quantum_export_${new Date().toISOString().slice(0, 10)}.md`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        toast.success("Markdown exported successfully")
    }

    return (
        <div className="h-full flex flex-col bg-paper overflow-hidden relative group font-serif transition-colors duration-500">
            {/* Minimal floating action bar - only show when needed */}
            {result && (stage === 'finished' || stage === 'generating') && (
                <div className="absolute top-4 right-4 z-10 flex gap-2">
                    <Button variant="outline" size="sm" className="h-7 text-xs gap-1 bg-white/80 backdrop-blur-sm" onClick={handleCopy}>
                        <Copy className="w-3 h-3" />
                        复制
                    </Button>
                    <Button variant="outline" size="sm" className="h-7 text-xs gap-1 bg-white/80 backdrop-blur-sm" onClick={handleExport}>
                        <Save className="w-3 h-3" />
                        导出
                    </Button>
                </div>
            )}

            {/* FIX: h-full + flex-1 + justify-center for absolute vertical centering */}
            <div className="flex-1 overflow-y-auto px-16 py-12 relative scroll-smooth flex flex-col">
                {stage === 'input' && !loading && (
                    // FIX: flex-1 + justify-center 实现绝对垂直居中
                    <div className="flex-1 flex flex-col items-center justify-center select-none space-y-6">
                        <div className="w-20 h-20 rounded-full bg-zinc-100/50 flex items-center justify-center ring-1 ring-zinc-200/50">
                            <Brain className="w-8 h-8 text-zinc-300 stroke-1" />
                        </div>
                        <div className="text-center space-y-2">
                            <p className="text-lg font-medium text-ink-primary">量子引擎已就绪</p>
                            <p className="text-sm text-ink-muted">请在左侧配置参数并点击 "开始创作"</p>
                        </div>
                    </div>
                )}

                {/* 2. Analyzer Loading */}
                {stage === 'analyzing' && (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-400 gap-6 animate-in fade-in duration-700">
                        <Brain className="w-8 h-8 text-zinc-300 stroke-1" />
                        <p className="text-sm font-mono text-zinc-500">Constructing narrative architecture...</p>
                    </div>
                )}

                {/* 3. Selection Grid */}
                {stage === 'selection' && (
                    <div className="grid grid-cols-1 gap-4 max-w-2xl mx-auto">
                        <h2 className="text-lg font-serif font-medium text-primary mb-2">Select Direction</h2>
                        {options.map((option) => (
                            <div
                                key={option.id}
                                onClick={() => handleGenerate(option)}
                                className="bg-white hover:bg-zinc-50 rounded-sm p-6 border border-zinc-200 hover:border-zinc-300 cursor-pointer transition-all group/card relative"
                            >
                                <div className="absolute top-6 right-6 opacity-0 group-hover/card:opacity-100 transition-opacity">
                                    <ArrowRight className="w-4 h-4 text-zinc-800" />
                                </div>
                                <h3 className="font-serif font-bold text-lg text-primary mb-2 group-hover/card:text-black transition-colors">
                                    {option.title}
                                </h3>
                                <div className="flex flex-wrap gap-2 mb-4">
                                    <span className="px-2 py-0.5 rounded-sm bg-zinc-100 text-zinc-600 text-[10px] font-medium border border-zinc-200">
                                        {option.hook_angle}
                                    </span>
                                    <span className="px-2 py-0.5 rounded-sm bg-zinc-100 text-zinc-600 text-[10px] font-medium border border-zinc-200">
                                        {option.target_audience}
                                    </span>
                                </div>
                                <div className="space-y-3">
                                    <p className="text-xs text-zinc-500 leading-relaxed font-sans">
                                        <span className="font-semibold text-zinc-700">Focus:</span> {option.pain_point}
                                    </p>
                                    <div className="mt-3 pt-3 border-t border-dashed border-zinc-200">
                                        <ul className="list-disc list-inside text-xs text-zinc-500 space-y-1 font-serif">
                                            {option.outline.slice(0, 3).map((point, i) => (
                                                <li key={i}>{point}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* 4. Generation Result - The 'Paper' View */}
                {(stage === 'generating' || stage === 'finished') && result ? (
                    <div className="prose prose-zinc prose-lg max-w-[65ch] mx-auto font-serif text-zinc-800 leading-relaxed">
                        <ReactMarkdown rehypePlugins={[rehypeSanitize, rehypeHighlight]}>{result}</ReactMarkdown>
                    </div>
                ) : (stage === 'generating') && (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-400 gap-4">
                        <PenTool className="w-8 h-8 text-zinc-300 animate-pulse stroke-1" />
                        <p className="text-sm font-mono text-zinc-500">Drafting manuscript...</p>
                    </div>
                )}
            </div>

            {/* Bottom Action Bar (Mobile/Quick Actions) - Optional or integrated into Layout */}
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
                {loading && (
                    <Button
                        onClick={handleStop}
                        variant="destructive"
                        className="shadow-xl rounded-full px-6"
                    >
                        <StopCircle className="w-4 h-4 mr-2" /> 停止生成
                    </Button>
                )}

            </div>
        </div>
    )
}

function Zap({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
    )
}
