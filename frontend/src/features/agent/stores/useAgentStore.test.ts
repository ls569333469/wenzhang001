import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act } from '@testing-library/react';

// Mock fetch globally
global.fetch = vi.fn();

describe('useAgentStore', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.resetModules();
    });

    describe('Initial State', () => {
        it('should have correct initial values', async () => {
            const { useAgentStore } = await import('@/features/agent/stores/useAgentStore');
            const state = useAgentStore.getState();

            expect(state.status).toBe('idle');
            expect(state.content).toBe('');
            expect(state.strategyOptions).toBeNull();
            expect(state.error).toBeNull();
            expect(state.isWaitingForSelection).toBe(false);
        });

        it('should have 4 timeline steps', async () => {
            const { useAgentStore } = await import('@/features/agent/stores/useAgentStore');
            const state = useAgentStore.getState();

            expect(state.steps).toHaveLength(4);
            expect(state.steps[0].agent).toBe('strategist');
            expect(state.steps[1].agent).toBe('writer');
            expect(state.steps[2].agent).toBe('critic');
            expect(state.steps[3].agent).toBe('polisher');
        });
    });

    describe('resetSession', () => {
        it('should reset state to initial values', async () => {
            const { useAgentStore } = await import('@/features/agent/stores/useAgentStore');

            // Modify state first
            act(() => {
                useAgentStore.setState({
                    status: 'writing',
                    content: 'Some content',
                    error: 'Some error',
                });
            });

            // Reset
            act(() => {
                useAgentStore.getState().resetSession();
            });

            const state = useAgentStore.getState();
            expect(state.status).toBe('idle');
            expect(state.content).toBe('');
            expect(state.error).toBeNull();
        });
    });

    describe('State Updates', () => {
        it('should allow setting status', async () => {
            const { useAgentStore } = await import('@/features/agent/stores/useAgentStore');

            act(() => {
                useAgentStore.setState({ status: 'connecting' });
            });

            expect(useAgentStore.getState().status).toBe('connecting');
        });

        it('should allow setting strategy options', async () => {
            const { useAgentStore } = await import('@/features/agent/stores/useAgentStore');

            const mockOptions = [
                { id: 1, title: 'Option A' },
                { id: 2, title: 'Option B' },
            ];

            act(() => {
                useAgentStore.setState({ strategyOptions: mockOptions });
            });

            expect(useAgentStore.getState().strategyOptions).toEqual(mockOptions);
        });
    });
});
