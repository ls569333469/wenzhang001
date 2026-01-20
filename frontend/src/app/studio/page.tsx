import { StudioLayout } from "@/features/studio/layout/StudioLayout";
import { ConfigIsland } from "@/features/studio/components/layout/ConfigIsland";
import { AgentIsland } from "@/features/studio/components/layout/AgentIsland";

/**
 * Studio Page - 组装页
 * 
 * 核心: 使用 StudioLayout 布局，传入左右 Island
 */
export default function StudioPage() {
    return (
        <StudioLayout
            leftPanel={<ConfigIsland />}
            rightPanel={<AgentIsland />}
        >
            {/* Layer 1: Central Canvas Content */}
            <div className="w-full max-w-3xl mx-auto space-y-8 animate-in fade-in zoom-in duration-500">

                {/* Paper Sheet (拟物化容器) */}
                <div className="min-h-[800px] bg-white rounded-xl shadow-sm border border-zinc-100 p-16">
                    <h1 className="font-serif text-4xl font-medium text-ink-primary mb-8 leading-tight placeholder:text-zinc-300 outline-none" contentEditable>
                        Untitled Research
                    </h1>
                    <div className="prose prose-zinc max-w-none">
                        <p className="text-zinc-500 italic">
                            Start writing or press <kbd className="font-sans bg-zinc-100 px-1 py-0.5 rounded text-xs border border-zinc-200">Cmd+K</kbd> to prompt agents...
                        </p>
                    </div>
                </div>

            </div>
        </StudioLayout>
    );
}
