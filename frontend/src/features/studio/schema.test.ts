import { describe, it, expect } from 'vitest';
import {
    GenerateRequestSchema,
    CreationConfigSchema,
    CreationModeSchema,
    WritingStyleSchema,
    ArticleLengthSchema,
} from './schema';

describe('Studio Schema', () => {
    describe('CreationConfigSchema', () => {
        it('should have correct default values', () => {
            const result = CreationConfigSchema.parse({});

            expect(result.mode).toBe('mid_article');  // P16: 默认中篇
            expect(result.style).toBe('professional');
        });
    });

    describe('CreationModeSchema', () => {
        it('should accept valid modes', () => {
            // P16: 新模式名
            expect(() => CreationModeSchema.parse('hot_take')).not.toThrow();
            expect(() => CreationModeSchema.parse('mid_article')).not.toThrow();
            expect(() => CreationModeSchema.parse('long_article')).not.toThrow();
            expect(() => CreationModeSchema.parse('bullish_take')).not.toThrow();
            expect(() => CreationModeSchema.parse('kaito_yap')).not.toThrow();
            expect(() => CreationModeSchema.parse('project_research')).not.toThrow();
            expect(() => CreationModeSchema.parse('tutorial')).not.toThrow();
            expect(() => CreationModeSchema.parse('binance_square')).not.toThrow();  // P34
        });

        it('should reject invalid modes', () => {
            expect(() => CreationModeSchema.parse('invalid')).toThrow();
            // P16: 旧模式名不再在 schema 中有效 (通过别名处理)
            expect(() => CreationModeSchema.parse('deep_analysis')).toThrow();
            expect(() => CreationModeSchema.parse('quick_summary')).toThrow();
        });
    });

    describe('WritingStyleSchema', () => {
        it('should accept valid styles including business styles', () => {
            expect(() => WritingStyleSchema.parse('professional')).not.toThrow();
            expect(() => WritingStyleSchema.parse('mimeng')).not.toThrow();
            expect(() => WritingStyleSchema.parse('banfo')).not.toThrow();
        });
    });

    describe('GenerateRequestSchema', () => {
        it('should validate a minimal valid request', () => {
            const validRequest = {
                prompt: 'Test input content',
                config: {},
            };

            const result = GenerateRequestSchema.safeParse(validRequest);
            expect(result.success).toBe(true);
        });

        it('should validate request with optional fields', () => {
            const validRequest = {
                prompt: 'Test input',
                config: { mode: 'mid_article', style: 'mimeng' },  // P16: 使用新模式名
                selected_option: {
                    id: 'opt-1',
                    title: 'Test Title',
                },
                info_anchors: {
                    must_mention: ['data1'],
                    key_data: ['key1'],
                    can_extend: ['extend1'],
                },
            };

            const result = GenerateRequestSchema.safeParse(validRequest);
            expect(result.success).toBe(true);
        });

        it('should reject empty prompt', () => {
            const invalidRequest = {
                prompt: '',
                config: {},
            };

            const result = GenerateRequestSchema.safeParse(invalidRequest);
            expect(result.success).toBe(false);
        });
    });
});
