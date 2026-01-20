'use client';

import Link from "next/link";
import { ArrowRight, Box, CreditCard, Layout } from "lucide-react";

/**
 * Design Lab Entrance
 * 
 * 展示 3 个风格变体，供用户选择
 */
export default function DesignLabPage() {
    return (
        <div className="min-h-screen bg-canvas flex flex-col items-center justify-center p-8">
            <div className="text-center mb-16 space-y-4">
                <h1 className="font-serif text-5xl font-medium text-ink-primary">
                    Design Laboratory
                </h1>
                <p className="text-ink-muted text-lg max-w-2xl mx-auto">
                    探索 Quantum Studio 的三种交互范式。
                    <br />
                    选择一个变体以进入沉浸式预览。
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl">

                {/* Variant A */}
                <VariantCard
                    href="/design-lab/variant-a"
                    title="The Athenaeum"
                    subtitle="Floating Islands"
                    icon={CreditCard}
                    desc="当前方案。高阶、悬浮、留白。将信息分层为独立的岛屿，减少认知负荷。"
                    color="bg-zinc-900"
                />

                {/* Variant B */}
                <VariantCard
                    href="/design-lab/variant-b"
                    title="The Workbench"
                    subtitle="Integrated Structure"
                    icon={Layout}
                    desc="经典生产力工具布局。侧边栏吸附，高密度信息展示，边界清晰。适合极客。"
                    color="bg-blue-600"
                />

                {/* Variant C */}
                <VariantCard
                    href="/design-lab/variant-c"
                    title="Zen Mode"
                    subtitle="Immersive Flow"
                    icon={Box}
                    desc="极致极简。移除一切边框，内容即 UI。完全沉浸的写作体验。"
                    color="bg-emerald-600"
                />

            </div>

            <div className="mt-16 text-xs text-ink-muted font-mono">
                Running on Tailwind v3.4.17 • Nuqs Active
            </div>
        </div>
    );
}

function VariantCard({ href, title, subtitle, icon: Icon, desc, color }: any) {
    return (
        <Link href={href} className="group relative bg-white rounded-3xl p-8 border border-zinc-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
            <div className={`absolute top-0 left-0 w-full h-1.5 ${color}`} />

            <div className="mb-6 flex items-center justify-between">
                <div className={`w-12 h-12 rounded-2xl ${color} bg-opacity-10 flex items-center justify-center text-zinc-900`}>
                    <Icon className="w-6 h-6 opacity-80" />
                </div>
                <div className="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center group-hover:bg-zinc-900 group-hover:text-white transition-colors">
                    <ArrowRight className="w-4 h-4" />
                </div>
            </div>

            <h3 className="text-xl font-serif font-bold text-zinc-900 mb-1">
                {title}
            </h3>
            <div className="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-4">
                {subtitle}
            </div>

            <p className="text-sm text-zinc-500 leading-relaxed">
                {desc}
            </p>
        </Link>
    );
}
