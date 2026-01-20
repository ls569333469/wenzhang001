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
    'deep_analysis',   // 深度分析
    'quick_summary',   // 快速摘要
    'rewrite',         // 改写润色
    'translate',       // 翻译
]);

/** 写作风格 */
export const WritingStyleSchema = z.enum([
    'professional',    // 专业投研
    'kol',             // KOL 观点
    'academic',        // 学术风格
    'casual',          // 轻松随意
]);

/** 目标字数 */
export const ArticleLengthSchema = z.enum([
    'short',           // 短文 (~500字)
    'medium',          // 中篇 (~1500字)
    'long',            // 长文 (~3000字)
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
    mode: CreationModeSchema.default('deep_analysis'),
    style: WritingStyleSchema.default('professional'),
    length: ArticleLengthSchema.default('medium'),
    knowledgeSources: z.array(z.string()).default([]),  // source IDs
    temperature: z.number().min(0).max(1).default(0.7),
    maxTokens: z.number().positive().default(4096),
});

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
