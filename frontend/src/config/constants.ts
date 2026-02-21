
import { CreationMode, ArticleLength, WritingStyle } from "@/features/studio/schema";

// 创作模式配置 (P27: 按使用频率排序)
export const CREATION_MODES: { id: CreationMode; title: string; desc?: string; compact?: boolean }[] = [
    {
        id: 'hot_take',
        title: '🔥 锐评',
        desc: '极简短评，3条候选，50-150字'
    },
    {
        id: 'bullish_take',
        title: '🌸 吹捧',
        desc: '正面解读，短评吹捧'
    },
    {
        id: 'short_article',
        title: '💬 短篇',
        desc: 'X正常发文，50-300字'
    },
    {
        id: 'mid_article',
        title: '📝 中篇',
        desc: '快速产出，要点突出，适合热点追踪'
    },
    {
        id: 'long_article',
        title: '📖 长篇',
        desc: '全面深度分析，长文结构，多角度论证'
    },
    {
        id: 'kaito_yap',
        title: '🎯 嘴撸',
        desc: '项目嘴撸，Mindshare 提升'
    },
    {
        id: 'tutorial',
        title: '📚 教程',
        compact: true
    },
    {
        id: 'project_research',
        title: '🔬 投研',
        compact: true
    }
];

// P27: 需要 DataPanel 的模式（有数据展示面板）
export const MODES_WITH_DATA_PANEL: CreationMode[] = [
    'bullish_take', 'kaito_yap', 'project_research'
];

// P11: 文章长度配置 (新篇幅体系)
export const ARTICLE_LENGTHS: { id: ArticleLength; label: string }[] = [
    { id: 'tweet', label: '推文 (~300字)' },
    { id: 'thread', label: '推文串 (~800字)' },
    { id: 'post', label: '帖子 (~1.5k字)' }
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
    inputLabel: '研究主题 / 指令',
    inputPlaceholder: '请输入您的研究主题或指令... (例如：分析 EIP-4844 对 Layer2 经济模型的影响)',
    startButton: '开始深度创作',
    stopButton: '停止生成',
    labels: {
        mode: '创作模式',
        style: '写作风格',
        length: '篇幅长度',
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
        studio: '创作中心',
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
