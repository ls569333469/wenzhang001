import { describe, it, expect } from 'vitest';
import { cn } from './utils';

describe('Utils', () => {
    describe('cn (classnames utility)', () => {
        it('should merge class names', () => {
            expect(cn('foo', 'bar')).toBe('foo bar');
        });

        it('should handle conditional classes', () => {
            expect(cn('base', true && 'active', false && 'hidden')).toBe('base active');
        });

        it('should handle undefined and null', () => {
            expect(cn('base', undefined, null, 'end')).toBe('base end');
        });

        it('should handle tailwind class conflicts (merge)', () => {
            // tailwind-merge should pick the last conflicting class
            expect(cn('p-4', 'p-2')).toBe('p-2');
            expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500');
        });

        it('should handle array of classes', () => {
            expect(cn(['foo', 'bar'])).toBe('foo bar');
        });
    });
});
