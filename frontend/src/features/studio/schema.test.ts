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

            expect(result.mode).toBe('deep_analysis');
            expect(result.style).toBe('professional');
            expect(result.length).toBe('medium');
            expect(result.temperature).toBe(0.7);
            expect(result.topP).toBe(0.9);
            expect(result.maxTokens).toBe(4096);
        });
    });

    describe('CreationModeSchema', () => {
        it('should accept valid modes', () => {
            expect(() => CreationModeSchema.parse('deep_analysis')).not.toThrow();
            expect(() => CreationModeSchema.parse('quick_summary')).not.toThrow();
            expect(() => CreationModeSchema.parse('rewrite')).not.toThrow();
        });

        it('should reject invalid modes', () => {
            expect(() => CreationModeSchema.parse('invalid')).toThrow();
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
                config: { mode: 'deep_analysis', style: 'mimeng' },
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
