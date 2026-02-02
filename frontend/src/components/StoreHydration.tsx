'use client';

/**
 * P14-B: Store Hydration Component
 * 
 * With skipHydration: true, stores need explicit rehydration on client mount.
 * This component handles that in a single place.
 */

import { useEffect } from 'react';
import { useAgentModelStore } from '@/features/agent/stores/useAgentModelStore';
import { useModeWriterStore } from '@/features/agent/stores/useModeWriterStore';

export function StoreHydration() {
    useEffect(() => {
        // Rehydrate all persistent stores on client mount
        useAgentModelStore.persist.rehydrate();
        useModeWriterStore.persist.rehydrate();
    }, []);

    return null; // This component renders nothing
}
