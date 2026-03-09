'use client';

import { AgentTimeline, TimelineStep } from "../timeline/AgentTimeline";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { useResearchStore } from "@/features/research/useResearchStore";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";

// P34: 投研流水线步骤定义
const RESEARCH_STEPS: TimelineStep[] = [
    { id: 'r-scout', agent: 'researcher', label: '侦察官', status: 'idle', message: '等待开始' },
    { id: 'r-strategist', agent: 'strategist', label: '策略官', status: 'idle', message: '等待侦察' },
    { id: 'r-enrichment', agent: 'researcher', label: '数据回填', status: 'idle', message: '等待分析' },
    { id: 'r-reviewer', agent: 'critic', label: '质检官', status: 'idle', message: '等待回填' },
    { id: 'r-summarizer', agent: 'writer', label: '总结官', status: 'idle', message: '等待质检' },
    { id: 'r-tweet', agent: 'writer', label: '推文写手', status: 'idle', message: '等待总结' },
    { id: 'r-card', agent: 'polisher', label: '配图生成', status: 'idle', message: '等待推文' },
    { id: 'r-report', agent: 'polisher', label: '日报渲染', status: 'idle', message: '等待配图' },
];

// statusMessage → 步骤映射
const STEP_KEYWORDS: Record<string, string> = {
    '侦察': 'r-scout',
    'scout': 'r-scout',
    '策略': 'r-strategist',
    '分析': 'r-strategist',
    '回填': 'r-enrichment',
    'enrichment': 'r-enrichment',
    '质检': 'r-reviewer',
    'reviewer': 'r-reviewer',
    '总结': 'r-summarizer',
    'summarizer': 'r-summarizer',
    '推文': 'r-tweet',
    'tweet': 'r-tweet',
    '配图': 'r-card',
    'card': 'r-card',
    '渲染': 'r-report',
    '日报': 'r-report',
    'report': 'r-report',
    '回写': 'r-report',
};

function getResearchSteps(statusMessage: string, isGenerating: boolean): TimelineStep[] {
    if (!isGenerating && !statusMessage) return RESEARCH_STEPS;

    const steps = RESEARCH_STEPS.map(s => ({ ...s }));

    // 根据 statusMessage 关键词判断当前步骤
    let activeStepId = '';
    const msg = statusMessage.toLowerCase();
    for (const [keyword, stepId] of Object.entries(STEP_KEYWORDS)) {
        if (msg.includes(keyword)) {
            activeStepId = stepId;
            break;
        }
    }

    if (activeStepId) {
        let found = false;
        for (const step of steps) {
            if (step.id === activeStepId) {
                step.status = 'active';
                step.message = statusMessage;
                found = true;
            } else if (!found) {
                step.status = 'completed';
                step.message = '完成';
            }
            // 后面的保持 idle
        }
    }

    // 全部完成
    if (!isGenerating && statusMessage.includes('完成')) {
        steps.forEach(s => { s.status = 'completed'; s.message = '完成'; });
    }

    return steps;
}

export function ProgressTab() {
    const searchParams = useSearchParams();
    const mode = searchParams.get('mode');
    const isResearchMode = mode === 'project_research';

    // Studio 模式数据
    const { steps: studioSteps, agentLogs } = useAgentStore();

    // 投研模式数据
    const statusMessage = useResearchStore((s) => s.statusMessage);
    const isGenerating = useResearchStore((s) => s.isGenerating);

    const handleViewThinking = () => {
        toast.info("思维链功能暂时不可用");
    };

    if (isResearchMode) {
        const researchSteps = getResearchSteps(statusMessage, isGenerating);
        return (
            <div className="space-y-4">
                <div className="text-sm font-semibold text-ink-primary mb-2">
                    投研流水线进度
                </div>
                <AgentTimeline
                    steps={researchSteps}
                    agentLogs={[]}
                />
                {statusMessage && (
                    <div className="mt-3 px-3 py-2 bg-zinc-50 rounded-lg text-xs text-ink-muted">
                        {statusMessage}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="text-sm font-semibold text-ink-primary mb-2">
                智能体执行进度
            </div>
            <AgentTimeline
                steps={studioSteps}
                agentLogs={agentLogs}
            />
        </div>
    );
}
