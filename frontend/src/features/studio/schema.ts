/**
 * Quantum Studio Schema - Single Source of Truth
 * 
 * 使用 Zod 定义所有核心数据结构
 * 类型通过 z.infer<typeof Schema> 自动生成
 * 
 * @version 9.0 - Vibe Coding Edition
 */

import { z } from 'zod';

// ===== 创作配置 Schema =====

/** 创作模式 (P18: 全模块独立架构, P27: +3 业务模式) */
export const CreationModeSchema = z.enum([
    'hot_take',           // 锐评 (50-150字)
    'short_article',      // 短篇 (200-500字)
    'mid_article',        // 中篇 (150-800字)
    'long_article',       // 长篇 (900-1800字)
    'tutorial',           // 教程 (400-1500字)
    'bullish_take',       // P27: 吹捧 (50-500字)
    'kaito_yap',          // P27: Kaito 嘴撸 (50-500字)
    'project_research',   // P27: 项目投研
]);

/** 写作风格 */
export const WritingStyleSchema = z.enum([
    'professional',    // 专业投研 (Default)
    'casual',          // 轻松随意
    // Business Styles (from src/lib/styles.ts)
    'mimeng',          // 咪蒙体
    'banfo',           // 半佛体
    'xinshixiang',     // 新世相体
    'shijuezhi',       // 视觉志体
    'lianbushou',      // 链捕手体
    'lingongzi',       // 临公子体
    'fengqiongzi',     // 风茕子体
    'chengshian',      // 程十安体
]);

/** P11/P16: 篇幅类型 (auto=用模式默认, custom=自定义字数) */
export const LengthTypeSchema = z.enum(['auto', 'custom']);
export type LengthType = z.infer<typeof LengthTypeSchema>;

/** P20: 时效性类型 (事件脉络感知) */
export const TimelinessSchema = z.enum(['realtime', 'recent', 'historical']);
export type Timeliness = z.infer<typeof TimelinessSchema>;

/** P20: 时效性选项 */
export const TIMELINESS_OPTIONS = [
    { value: 'realtime', label: '今天/刚发生', icon: '⚡' },
    { value: 'recent', label: '近几天', icon: '📅' },
    { value: 'historical', label: '更早/复盘', icon: '📜' },
] as const;

/** @deprecated P11: 旧篇幅体系，已过期，保留用于后端兼容 */
export const ArticleLengthSchema = z.enum([
    'tweet',           // 推文 (~300字)
    'thread',          // 推文串 (~800字)
    'post',            // 帖子 (~1.5k字)
]);

/** 知识来源 */
export const KnowledgeSourceSchema = z.object({
    id: z.string(),
    name: z.string(),
    type: z.enum(['google_sheets', 'local', 'url']),
    docCount: z.number(),
    lastSync: z.string().datetime().optional(),
});

/** 完整创作配置 */
export const CreationConfigSchema = z.object({
    mode: CreationModeSchema.default('mid_article'),
    style: WritingStyleSchema.default('mimeng'),  // P28: 默认咪蒙，有 Google Sheets 数据
    length_type: LengthTypeSchema.default('auto'),  // P16: 篇幅类型
    custom_length: z.number().min(50).max(5000).optional(),  // P16: 自定义字数
    knowledgeSources: z.array(z.string()).default([]),  // source IDs
});

// ===== P13: API 配置 Schema =====

/** AI 提供商 */
export const AIProviderSchema = z.enum(['volcengine', 'google', 'grok']);

/** 单个 API 配置 */
export const APIConfigSchema = z.object({
    provider: AIProviderSchema.default('volcengine'),
    model_id: z.string().optional(),
    api_key: z.string().optional(),
});

// P14-B: Provider ID 常量 (前后端共用，防止拼写错误)
export const PROVIDER_IDS = {
    VOLCENGINE: 'volcengine',
    GOOGLE: 'google',
    GROK: 'grok',
} as const;

/** Agent 模型配置项 (必须包含 provider 和 model) */
export const AgentModelSettingSchema = z.object({
    provider: AIProviderSchema,
    model: z.string(),
});

/** P14-B: 智能体团队模型分配 */
export const AgentModelsSchema = z.object({
    strategist: AgentModelSettingSchema,
    writer: AgentModelSettingSchema,
    critic: AgentModelSettingSchema,
    polisher: AgentModelSettingSchema,
});

/** P14-B: 默认 Agent 模型配置 (默认使用火山引擎豆包模型) */
export const DEFAULT_AGENT_MODELS: z.infer<typeof AgentModelsSchema> = {
    strategist: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    writer: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    critic: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    polisher: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
};

export type AgentModels = z.infer<typeof AgentModelsSchema>;
export type AgentModelSetting = z.infer<typeof AgentModelSettingSchema>;

// ===== P14-C: 模式专属 Writer 配置 =====

/** 可配置 Writer 的模式列表 */
export const MODE_WRITER_IDS = {
    HOT_TAKE: 'hot_take',
    SHORT_ARTICLE: 'short_article',
    MID_ARTICLE: 'mid_article',
    LONG_ARTICLE: 'long_article',
    TUTORIAL: 'tutorial',
    BULLISH_TAKE: 'bullish_take',
    KAITO_YAP: 'kaito_yap',
    PROJECT_RESEARCH: 'project_research',
} as const;

/** 模式 Writer 配置 Schema */
export const ModeWriterConfigSchema = z.object({
    hot_take: AgentModelSettingSchema,
    short_article: AgentModelSettingSchema,
    mid_article: AgentModelSettingSchema,
    long_article: AgentModelSettingSchema,
    tutorial: AgentModelSettingSchema,
    bullish_take: AgentModelSettingSchema,
    kaito_yap: AgentModelSettingSchema,
    project_research: AgentModelSettingSchema,
});

/** P14-C: 默认模式 Writer 配置 */
export const DEFAULT_MODE_WRITERS: z.infer<typeof ModeWriterConfigSchema> = {
    hot_take: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    short_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    mid_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
    long_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
    tutorial: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
    bullish_take: { provider: PROVIDER_IDS.GROK, model: 'grok-4-1-fast-reasoning' },
    kaito_yap: { provider: PROVIDER_IDS.GROK, model: 'grok-4-1-fast-reasoning' },
    project_research: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
};

export type ModeWriterConfig = z.infer<typeof ModeWriterConfigSchema>;

// ===== P24-D: 统一 4 智能体 × 6 模式配置 =====

/** P24-D: 跳过逻辑 — 某些模式不需要特定 agent */
export const SKIP_MODES = {
    strategist: [] as string[],
    writer: [] as string[],
    critic: ['hot_take', 'kaito_yap'],
    polisher: ['hot_take', 'kaito_yap'],
} as const;

/** 完整模式 Schema（4 个 agent 通用, P27: 8 模式） */
const FullModeConfigSchema = z.object({
    hot_take: AgentModelSettingSchema,
    short_article: AgentModelSettingSchema,
    mid_article: AgentModelSettingSchema,
    long_article: AgentModelSettingSchema,
    tutorial: AgentModelSettingSchema,
    bullish_take: AgentModelSettingSchema,
    kaito_yap: AgentModelSettingSchema,
    project_research: AgentModelSettingSchema,
});

/** P24-D: 模式专属 Strategist 配置 */
export const ModeStrategistConfigSchema = FullModeConfigSchema;
export const DEFAULT_MODE_STRATEGISTS: z.infer<typeof ModeStrategistConfigSchema> = {
    hot_take: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    short_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    mid_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    long_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    tutorial: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    bullish_take: { provider: PROVIDER_IDS.GROK, model: 'grok-4-1-fast-reasoning' },
    kaito_yap: { provider: PROVIDER_IDS.GROK, model: 'grok-4-1-fast-reasoning' },
    project_research: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
};
export type ModeStrategistConfig = z.infer<typeof ModeStrategistConfigSchema>;

/** P24-D: 模式专属 Critic 配置（短内容模式跳过） */
export const ModeCriticConfigSchema = FullModeConfigSchema;
export const DEFAULT_MODE_CRITICS: z.infer<typeof ModeCriticConfigSchema> = {
    hot_take: { provider: PROVIDER_IDS.VOLCENGINE, model: '' },  // skip
    short_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    mid_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    long_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    tutorial: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    bullish_take: { provider: PROVIDER_IDS.VOLCENGINE, model: '' },  // skip
    kaito_yap: { provider: PROVIDER_IDS.VOLCENGINE, model: '' },  // skip
    project_research: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
};
export type ModeCriticConfig = z.infer<typeof ModeCriticConfigSchema>;

/** P24-D: 模式专属 Polisher 配置（短内容模式跳过） */
export const ModePolisherConfigSchema = FullModeConfigSchema;
export const DEFAULT_MODE_POLISHERS: z.infer<typeof ModePolisherConfigSchema> = {
    hot_take: { provider: PROVIDER_IDS.VOLCENGINE, model: '' },  // skip
    short_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },  // P26: enabled
    mid_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    long_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    tutorial: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
    bullish_take: { provider: PROVIDER_IDS.VOLCENGINE, model: '' },  // skip
    kaito_yap: { provider: PROVIDER_IDS.VOLCENGINE, model: '' },  // skip
    project_research: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-2-0-lite-260215' },
};
export type ModePolisherConfig = z.infer<typeof ModePolisherConfigSchema>;

// ===== 智能体状态 Schema =====

/** Agent 角色 */
export const AgentRoleSchema = z.enum([
    'strategist',      // 策略师
    'researcher',      // 研究员
    'writer',          // 写作者
    'critic',          // 评审员
    'polisher',        // 润色师 (P24: 补全)
]);

/** Agent 状态 */
export const AgentStatusSchema = z.object({
    agent: AgentRoleSchema,
    status: z.enum(['idle', 'active', 'completed', 'error']),
    message: z.string().optional(),
    progress: z.number().min(0).max(100).optional(),
    startedAt: z.string().datetime().optional(),
    completedAt: z.string().datetime().optional(),
});

// ===== 生成请求/响应 Schema =====

/** 生成请求 */
export const GenerateRequestSchema = z.object({
    prompt: z.string().min(1, '请输入创作素材'),
    config: CreationConfigSchema,
    // Phase 9: Two-stage workflow fields
    selected_option: z.any().optional(),
    info_anchors: z.object({
        must_mention: z.array(z.string()),
        key_data: z.array(z.string()),
        can_extend: z.array(z.string()),
    }).optional(),
});

/** 生成结果 */
export const GenerateResultSchema = z.object({
    id: z.string().uuid(),
    content: z.string(),
    wordCount: z.number(),
    tokenCount: z.number(),
    createdAt: z.string().datetime(),
    config: CreationConfigSchema,
});

/** 流式输出块 */
export const StreamChunkSchema = z.object({
    type: z.enum(['content', 'agent_update', 'log', 'done', 'error']),
    data: z.union([
        z.string(),                    // content
        AgentStatusSchema,             // agent_update
        z.object({ message: z.string() }), // log/error
    ]),
});

// ===== 工作台状态 Schema =====

/** 工作台状态 */
export const WorkbenchStateSchema = z.object({
    status: z.enum(['idle', 'configuring', 'generating', 'complete', 'error']),
    config: CreationConfigSchema,
    prompt: z.string().default(''),
    result: GenerateResultSchema.nullable().default(null),
    agents: z.array(AgentStatusSchema).default([]),
    logs: z.array(z.string()).default([]),
    error: z.string().nullable().default(null),
});

// ===== 自动生成 TypeScript 类型 =====

export type CreationMode = z.infer<typeof CreationModeSchema>;
export type WritingStyle = z.infer<typeof WritingStyleSchema>;
export type ArticleLength = z.infer<typeof ArticleLengthSchema>;
export type KnowledgeSource = z.infer<typeof KnowledgeSourceSchema>;
export type CreationConfig = z.infer<typeof CreationConfigSchema>;
export type AgentRole = z.infer<typeof AgentRoleSchema>;
export type AgentStatus = z.infer<typeof AgentStatusSchema>;
export type GenerateRequest = z.infer<typeof GenerateRequestSchema>;
export type GenerateResult = z.infer<typeof GenerateResultSchema>;
export type StreamChunk = z.infer<typeof StreamChunkSchema>;
export type WorkbenchState = z.infer<typeof WorkbenchStateSchema>;
// P13: API 配置类型
export type AIProvider = z.infer<typeof AIProviderSchema>;
export type APIConfig = z.infer<typeof APIConfigSchema>;

// ===== 默认值工厂 =====

export const defaultConfig: CreationConfig = CreationConfigSchema.parse({});

export const defaultWorkbenchState: WorkbenchState = WorkbenchStateSchema.parse({
    status: 'idle',
    config: defaultConfig,
});

// ===== 验证辅助函数 =====

export function validateConfig(data: unknown): CreationConfig {
    return CreationConfigSchema.parse(data);
}

export function validateRequest(data: unknown): GenerateRequest {
    return GenerateRequestSchema.parse(data);
}

export function safeParseConfig(data: unknown) {
    return CreationConfigSchema.safeParse(data);
}
