"use client";

import React from "react";
import { PenTool, Library, Settings2 } from "lucide-react";
import { MonitorCard } from "@/features/dashboard/components/MonitorCard";
import { ActionTile } from "@/features/dashboard/components/ActionTile";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-4xl mx-auto px-8 py-16 space-y-12">
        {/* 欢迎语 */}
        <header className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-serif text-ink-primary tracking-tight">
            晚上好，架构师。
          </h1>
          <p className="text-ink-muted text-sm md:text-base">
            Quantum Studio v6.1 — The Athenaeum
          </p>
        </header>

        {/* 系统状态 */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-zinc-200"></div>
            <span className="text-[10px] font-semibold tracking-widest text-ink-muted uppercase">
              系统状态
            </span>
            <div className="h-px flex-1 bg-zinc-200"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <MonitorCard label="后端核心" status="online" latency="12ms" />
            <MonitorCard label="知识库引擎" status="offline" />
          </div>
        </section>

        {/* 快速操作 */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-zinc-200"></div>
            <span className="text-[10px] font-semibold tracking-widest text-ink-muted uppercase">
              快速操作
            </span>
            <div className="h-px flex-1 bg-zinc-200"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ActionTile
              icon={PenTool}
              title="开始创作"
              description="使用量子引擎起草新内容。"
              href="/studio"
            />
            <ActionTile
              icon={Library}
              title="知识库管理"
              description="管理来自飞书的素材。"
              href="/knowledge"
            />
            <ActionTile
              icon={Settings2}
              title="系统设置"
              description="配置 API 密钥与模型参数。"
              href="/settings"
            />
          </div>
        </section>
      </div>
    </div>
  );
}
