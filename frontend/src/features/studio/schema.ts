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

/** 创作模式 */
export const CreationModeSchema = z.enum([
    'hot_take',        // P14: 锐评模式
    'mid_article',     // P16: 中篇 (原 quick_summary)
    'long_article',    // P16: 长篇 (原 deep_analysis)
    'rewrite',         // 改写润色
    'tutorial',        // P13: 教程模式
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
    type: z.enum(['lark', 'local', 'url']),
    docCount: z.number(),
    lastSync: z.string().datetime().optional(),
});

/** 完整创作配置 */
export const CreationConfigSchema = z.object({
    mode: CreationModeSchema.default('mid_article'),
    style: WritingStyleSchema.default('professional'),
    length_type: LengthTypeSchema.default('auto'),  // P16: 篇幅类型
    custom_length: z.number().min(50).max(5000).optional(),  // P16: 自定义字数
    length: ArticleLengthSchema.default('thread').optional(),  // @deprecated: 旧字段，向后兼容
    knowledgeSources: z.array(z.string()).default([]),  // source IDs
    temperature: z.number().min(0).max(1).default(0.7),
    topP: z.number().min(0).max(1).default(0.9),
    maxTokens: z.number().positive().default(4096),
    retention_level: z.number().min(1).max(5).default(3),  // P10: 保留度等级 1-5
});

// ===== P13: API 配置 Schema =====

/** AI 提供商 */
export const AIProviderSchema = z.enum(['volcengine', 'google']);

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
    strategist: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-1-8-251228' },
    writer: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-1-8-251228' },
    critic: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-1-8-251228' },
    polisher: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-1-8-251228' },
};

export type AgentModels = z.infer<typeof AgentModelsSchema>;
export type AgentModelSetting = z.infer<typeof AgentModelSettingSchema>;

// ===== P14-C: 模式专属 Writer 配置 =====

/** 可配置 Writer 的模式列表 */
export const MODE_WRITER_IDS = {
    HOT_TAKE: 'hot_take',
    MID_ARTICLE: 'mid_article',
    LONG_ARTICLE: 'long_article',
    TUTORIAL: 'tutorial',
    REWRITE: 'rewrite',
} as const;

/** 模式别名映射 (用于兼容旧数据) */
export const MODE_ALIASES: Record<string, string> = {
    'mid_take': 'mid_article',         // 历史别名
    'quick_summary': 'mid_article',    // P16: 快讯速评→中篇
    'deep_analysis': 'long_article',   // P16: 深度分析→长篇
};

/** 模式 Writer 配置 Schema */
export const ModeWriterConfigSchema = z.object({
    hot_take: AgentModelSettingSchema,
    mid_article: AgentModelSettingSchema,
    long_article: AgentModelSettingSchema,
    tutorial: AgentModelSettingSchema,
    rewrite: AgentModelSettingSchema,
});

/** P14-C: 默认模式 Writer 配置 */
export const DEFAULT_MODE_WRITERS: z.infer<typeof ModeWriterConfigSchema> = {
    hot_take: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-1-8-251228' },
    mid_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
    long_article: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
    tutorial: { provider: PROVIDER_IDS.VOLCENGINE, model: 'deepseek-v3-2-251201' },
    rewrite: { provider: PROVIDER_IDS.VOLCENGINE, model: 'doubao-seed-1-8-251228' },
};

export type ModeWriterConfig = z.infer<typeof ModeWriterConfigSchema>;

// ===== 智能体状态 Schema =====

/** Agent 角色 */
export const AgentRoleSchema = z.enum([
    'strategist',      // 策略师
    'researcher',      // 研究员
    'writer',          // 写作者
    'critic',          // 评审员
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
