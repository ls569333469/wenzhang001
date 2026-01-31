
import { CreationMode, ArticleLength, WritingStyle } from "@/features/studio/schema";

// 创作模式配置 (P10 简化版)
export const CREATION_MODES: { id: CreationMode; title: string; desc?: string; compact?: boolean }[] = [
    {
        id: 'deep_analysis',
        title: '深度分析',
        desc: '全面深度分析，长文结构，多角度论证'
    },
    {
        id: 'quick_summary',
        title: '快讯速评',
        desc: '快速产出，要点突出，适合热点追踪'
    },
    {
        id: 'rewrite',
        title: '改写润色',
        desc: '基于原文改写，保持核心信息',
        compact: true
    },
    {
        id: 'translate',
        title: '教程指南',
        desc: '步骤清晰，可操作性强',
        compact: true
    }
];

// P11: 文章长度配置 (新篇幅体系)
export const ARTICLE_LENGTHS: { id: ArticleLength; label: string }[] = [
    { id: 'tweet', label: '推文 (~300字)' },
    { id: 'thread', label: '推文串 (~800字)' },
    { id: 'post', label: '帖子 (~1.5k字)' }
];

// P10-3: 开头Hook强度配置
export const HOOK_INTENSITIES = [
    { id: 'gentle', label: '温和开头', desc: '平稳叙述，娓娓道来', value: 1 },
    { id: 'standard', label: '标准开头', desc: '有力开场，引人入胜', value: 2 },
    { id: 'strong', label: '强力Hook', desc: '制造悬念，情绪渲染', value: 3 },
    { id: 'explosive', label: '爆款开场', desc: '冲击性开局，极度抓眼球', value: 4 },
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
        hookIntensity: '开头吸引力',
        temperature: '创意程度 (随机性)',
        topP: '思维发散度 (Top P)',
        maxTokens: '最大长度 (Tokens)',
        knowledge: '知识库'
    },
    // New: Agent Flow localization
    agentFlow: {
        title: '智能体流程',
        strategist: '策略分析',
        writer: '初稿撰写',
        critic: '质量审核',
        polisher: '润色打磨'
    },
    // New: Status messages
    status: {
        idle: '等待开始',
        thinking: '思考中...',
        processing: '处理中...',
        completed: '已完成',
        error: '出错了'
    },
    // New: Navigation labels
    nav: {
        studio: '创作工坊',
        knowledge: '知识库',
        agents: '智能体',
        settings: '系统设置',
        dashboard: '控制台'
    },
    // New: Monitor card text
    monitor: {
        operational: '运行正常',
        offline: '服务离线',
        connectionFailed: '连接失败',
        latencyLabel: '延迟',
        backendCore: '后端核心',
        knowledgeEngine: '知识库引擎'
    },
    // New: Multi-turn dialogue
    actions: {
        continueGenerate: '继续生成',
        regenerate: '重新生成',
        copyContent: '复制内容',
        exportMarkdown: '导出 Markdown'
    },
    // New: HeroInput specific
    heroInput: {
        aiEnhanced: 'AI 增强',
        keyboardHint: '⌘ + Enter 发送',
        suggestionPrefix: '尝试输入:'
    }
};
