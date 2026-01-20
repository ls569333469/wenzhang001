
import { CreationMode, ArticleLength, WritingStyle } from "@/features/studio/schema";

// 创作模式配置
export const CREATION_MODES: { id: CreationMode; title: string; desc?: string; compact?: boolean }[] = [
    {
        id: 'deep_analysis',
        title: '深度分析',
        desc: '全面调研，逻辑严密，适合研报'
    },
    {
        id: 'quick_summary',
        title: '快速摘要',
        desc: '提炼核心观点，适合早报'
    },
    {
        id: 'rewrite',
        title: '改写润色',
        compact: true
    },
    {
        id: 'translate',
        title: '专业翻译',
        compact: true
    }
];

// 文章长度配置
export const ARTICLE_LENGTHS: { id: ArticleLength; label: string }[] = [
    { id: 'short', label: '短篇 (~500字)' },
    { id: 'medium', label: '中篇 (~1.5k字)' },
    { id: 'long', label: '长文 (~3k字)' }
];

// Web3 知识库配置
export const WEB3_KNOWLEDGE_BASES = [
    { id: 'auto', name: '✨ 智能匹配 (Auto)', count: 0 },
    { id: 'kb-defi', name: 'DeFi 进展与分析', count: 124 },
    { id: 'kb-meme', name: 'MemeCoin 研究所', count: 85 },
    { id: 'kb-layer2', name: 'Layer2 观察', count: 56 },
    { id: 'kb-nft', name: 'NFT & Metaverse', count: 42 },
    { id: 'kb-infra', name: 'Web3 Infrastructure', count: 38 },
    { id: 'kb-macro', name: 'Macro Economics', count: 21 },
    { id: 'kb-reg', name: 'Regulatory Policy', count: 15 },
];

// 默认提示词模板 (For Settings MVP)
export const DEFAULT_PROMPTS = {
    strategist: `Role: You are The Strategist.
Task: Analyze source material and create a content plan.
Output: JSON with info_anchors and 3 strategy options.`,
    writer: `Role: You are The Writer.
Task: Write the FULL CONTENT article based on the Strategist's plan.
Requirements: Strictly follow the outline. Use Chinese.`,
    critic: `Role: You are The Chief Editor.
Task: Score the content (0-100) and give feedback.`
};

// 本地化 UI 文本
export const UI_TEXT = {
    panelTitle: '创作配置',
    panelDesc: '定义 AI 的思考模式与输出风格',
    coreSettings: '✨ 核心配置',
    knowledgeBase: '🧠 知识库选择',
    advancedSettings: '⚡ 高级模型设置',
    inputLabel: '研究主题 / 指令',
    inputPlaceholder: '请输入您的研究主题或指令... (例如：分析 EIP-4844 对 Layer2 经济模型的影响)',
    startButton: '开始深度创作',
    stopButton: '停止生成',
    labels: {
        mode: '创作模式',
        style: '写作风格',
        length: '篇幅长度',
        temperature: '创意程度 (随机性)',
        topP: '思维发散度 (Top P)',
        maxTokens: '最大长度 (Tokens)',
        knowledge: '知识库'
    }
};
