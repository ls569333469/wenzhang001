'use client';

import * as React from 'react';
import { AgentInspector } from "@/features/workbench/components/AgentInspector";
import { WritingCanvas } from "@/features/workbench/components/WritingCanvas";
import { Sliders, BookOpen, FileText, Zap, ChevronDown } from "lucide-react";

/**
 * Studio Page: The "Production Workshop" of Quantum Studio
 * v6.2 - Phase 3.6: Responsive Gravity (Visual Balance)
 * Implements locked height + vertical centering
 */
export default function StudioPage() {
  return (
    // FIX: 强制占满剩余屏幕高度，并锁定溢出
    <div className="flex h-full overflow-hidden">
      {/* Left: Config Panel (280px) */}
      <aside className="w-[280px] border-r border-hairline bg-surface flex flex-col overflow-hidden shrink-0">
        {/* Header */}
        <div className="h-14 flex items-center px-4 border-b border-hairline shrink-0">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-ink-muted" />
            <span className="text-sm font-medium text-ink-primary">创作配置</span>
          </div>
        </div>

        {/* Config Content - 弹性伸缩 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Mode Selector */}
          <div className="space-y-2">
            <label className="text-[10px] font-semibold text-ink-muted uppercase tracking-wider">
              创作模式
            </label>
            <button className="w-full flex items-center justify-between px-3 py-2 bg-surface border border-hairline rounded-sm text-sm text-ink-primary hover:border-zinc-300 transition-colors">
              <span>深度分析</span>
              <ChevronDown className="w-4 h-4 text-ink-muted" />
            </button>
          </div>

          {/* Style Selector */}
          <div className="space-y-2">
            <label className="text-[10px] font-semibold text-ink-muted uppercase tracking-wider">
              写作风格
            </label>
            <button className="w-full flex items-center justify-between px-3 py-2 bg-surface border border-hairline rounded-sm text-sm text-ink-primary hover:border-zinc-300 transition-colors">
              <span>专业投研</span>
              <ChevronDown className="w-4 h-4 text-ink-muted" />
            </button>
          </div>

          {/* Length Selector */}
          <div className="space-y-2">
            <label className="text-[10px] font-semibold text-ink-muted uppercase tracking-wider">
              目标字数
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button className="px-3 py-2 text-xs border border-hairline rounded-sm text-ink-muted hover:border-zinc-300 transition-colors">
                短文
              </button>
              <button className="px-3 py-2 text-xs border border-zinc-400 rounded-sm text-ink-primary bg-zinc-100 font-medium">
                中篇
              </button>
              <button className="px-3 py-2 text-xs border border-hairline rounded-sm text-ink-muted hover:border-zinc-300 transition-colors">
                长文
              </button>
            </div>
          </div>

          {/* Knowledge Source */}
          <div className="space-y-2">
            <label className="text-[10px] font-semibold text-ink-muted uppercase tracking-wider">
              知识来源
            </label>
            <div className="space-y-2">
              <div className="flex items-center gap-2 p-2 border border-hairline rounded-sm">
                <BookOpen className="w-4 h-4 text-ink-muted" />
                <span className="text-xs text-ink-primary flex-1">知识库 (Lark)</span>
                <span className="text-[10px] text-emerald-600 font-medium">303 条</span>
              </div>
              <div className="flex items-center gap-2 p-2 border border-hairline rounded-sm">
                <FileText className="w-4 h-4 text-ink-muted" />
                <span className="text-xs text-ink-primary flex-1">风格库</span>
                <span className="text-[10px] text-ink-muted">12 篇</span>
              </div>
            </div>
          </div>

          {/* Action Button - 跟随内容流 */}
          <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-zinc-800 text-zinc-50 rounded-sm hover:bg-zinc-700 transition-colors">
            <Zap className="w-4 h-4" />
            <span className="text-sm font-medium">开始创作</span>
          </button>
        </div>
      </aside>

      {/* Center: Canvas (Elastic) - 使用 h-full 确保子组件可垂直居中 */}
      <main className="flex-1 overflow-y-auto bg-paper/50 relative">
        <WritingCanvas />
      </main>

      {/* Right: Agent Inspector (320px) */}
      <aside className="w-[320px] border-l border-hairline bg-surface flex flex-col overflow-hidden shrink-0">
        <AgentInspector />
      </aside>
    </div>
  );
}
