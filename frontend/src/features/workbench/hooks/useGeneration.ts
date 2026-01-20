'use client'

import { useRef } from 'react'
import { useWorkbenchStore, StrategyOption } from '../stores/useWorkbenchStore'
import { API_BASE_URL } from '@/config/api'
import { toast } from "sonner"
import { Brain, PenTool, Gavel, Sparkles, type LucideIcon } from 'lucide-react'

// Constants
type AgentType = 'strategist' | 'writer' | 'critic' | 'polisher'
const AGENT_Defs: { id: AgentType; name: string; icon: LucideIcon }[] = [
    { id: 'strategist', name: 'Strategist', icon: Brain },
    { id: 'writer', name: 'Writer', icon: PenTool },
    { id: 'critic', name: 'Critic', icon: Gavel },
    { id: 'polisher', name: 'Polisher', icon: Sparkles },
]

export function useGeneration() {
    const store = useWorkbenchStore()
    const abortRef = useRef<AbortController | null>(null)

    // Helper: Reset Agent Steps
    const resetAgentSteps = (status: 'idle' | 'active' = 'idle') => {
        store.initAgents(AGENT_Defs.map(a => ({
            id: a.id,
            name: a.name,
            status: status === 'active' && a.id === 'strategist' ? 'active' : 'idle',
            icon: a.icon,
            logs: [],
            thinkingSteps: [],
            progress: 0
        })))
    }

    // Helper: Parse SSE
    const parseSSE = (line: string) => {
        if (!line.startsWith('data: ')) return null
        try {
            return JSON.parse(line.slice(6))
        } catch {
            return null
        }
    }

    // Helper: Get API Config
    const getApiConfig = () => {
        const apiKeys = JSON.parse(localStorage.getItem('quantumStudio_apiKeys') || '{}')
        const selectedModels = JSON.parse(localStorage.getItem('quantumStudio_selectedModels') || '{}')
        const agentModels = JSON.parse(localStorage.getItem('quantumStudio_agentModels') || '{}')
        const providerKeyMap: Record<string, string> = { google: 'gemini', volcengine: 'doubao', deepseek: 'deepseek', openai: 'openai' }

        const agentConfig: Record<string, { provider: string; api_key: string; model_id: string }> = {}
        Object.entries(agentModels).forEach(([agent, provider]) => {
            const pid = provider as string
            agentConfig[agent] = {
                provider: pid,
                api_key: apiKeys[providerKeyMap[pid] || pid] || '',
                model_id: selectedModels[pid] || ''
            }
        })
        return agentConfig
    }

    // --- Phase 1: Analyze ---
    const handleAnalyze = async () => {
        if (!store.input && store.references.length === 0) {
            toast.error("Please enter specific topic or reference")
            return
        }

        store.setLoading(true)
        store.setStage('analyzing')
        store.clearLogs()
        store.setResult('')
        store.setOptions([])

        resetAgentSteps('active')
        store.addLog("🔍 Strategist is starting analysis...")

        const controller = new AbortController()
        abortRef.current = controller

        const timeoutId = setTimeout(() => controller.abort(), 300000) // 5 min timeout

        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: store.input,
                    references: store.references.filter(r => r.trim() !== ''),
                    mode: store.mode,
                    narrative_type: store.narrativeType,
                    agent_config: getApiConfig()
                }),
                signal: controller.signal
            })

            clearTimeout(timeoutId)

            if (!response.ok) throw new Error(response.statusText)
            if (!response.body) throw new Error('No response body')

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    const data = parseSSE(line)
                    if (!data) continue

                    if (data.type === 'thinking_step') {
                        store.addAgentThinkingStep(data.agent, { step: data.step, content: data.detail || data.step })
                        store.addLog(`[${data.agent}] ${data.detail}`)
                    } else if (data.type === 'analysis_result') {
                        if (data.payload.error) throw new Error(data.payload.error)
                        store.setOptions(data.payload.options || [])
                        store.updateAgentStatus('strategist', 'completed')
                        store.setStage('selection')
                        store.addLog(`✅ Analysis complete. ${data.payload.options?.length} options generated.`)
                    } else if (data.type === 'agent_update') {
                        store.updateAgentStatus(data.step, data.status)
                        store.addLog(`✅ ${data.step} ${data.status}`)
                    } else if (data.type === 'error') throw new Error(data.message)
                }
            }
        } catch (e) {
            if (e instanceof Error && e.name === 'AbortError') {
                store.addLog('🛑 User stopped analysis.')
                toast.warning("Analysis stopped")
            } else {
                console.error(e)
                store.addLog(`Analysis Failed: ${e}`)
                toast.error(`Analysis Failed: ${e}`)
            }
        } finally {
            store.setLoading(false)
            abortRef.current = null
        }
    }

    // --- Phase 2: Generate ---
    const handleGenerate = async (option: StrategyOption) => {
        store.setLoading(true)
        store.setStage('generating')
        store.addLog(`🎯 Selected Option: ${option.title}`)

        // Reset Logic: Keep option, but reset agents
        store.initAgents(AGENT_Defs.map(a => ({ ...a, status: 'idle', logs: [], thinkingSteps: [], progress: 0, icon: a.icon })))

        const controller = new AbortController()
        abortRef.current = controller
        const timeoutId = setTimeout(() => controller.abort(), 300000)

        try {
            const response = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: store.input,
                    references: store.references.filter(r => r.trim() !== ''),
                    mode: store.mode,
                    narrative_type: store.narrativeType,
                    agent_config: getApiConfig(),
                    selected_option: option
                }),
                signal: controller.signal
            })

            clearTimeout(timeoutId)

            if (!response.ok) throw new Error(response.statusText)
            if (!response.body) throw new Error('No response body')

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    const data = parseSSE(line)
                    if (!data) continue

                    if (data.type === 'thinking_step') {
                        store.addAgentThinkingStep(data.agent, { step: data.step, content: data.detail || data.step })
                        store.addLog(`[${data.agent}] ${data.step}`)
                    } else if (data.type === 'agent_update') {
                        store.updateAgentStatus(data.step, data.status)
                        store.addLog(`✅ Agent State Update: ${data.step}`)
                    } else if (data.type === 'final_result') {
                        store.setResult(data.payload)
                        store.setStage('finished')
                        // Mark all active agents as completed
                        store.agentSteps.forEach(a => {
                            if (a.thinkingSteps.length > 0) store.updateAgentStatus(a.id, 'completed')
                        })
                    } else if (data.type === 'error') {
                        store.addLog(`❌ ${data.message}`)
                    }
                }
            }
        } catch (e) {
            if (e instanceof Error && e.name === 'AbortError') {
                store.addLog('🛑 User stopped generation.')
                toast.warning("Generation stopped")
            } else {
                console.error(e)
                store.addLog(`Generation Failed: ${e}`)
                toast.error("Generation Failed")
            }
        } finally {
            store.setLoading(false)
            abortRef.current = null
        }
    }

    const handleStop = () => {
        if (abortRef.current) {
            abortRef.current.abort()
        }
    }

    // Initial setup on mount if needed
    // useEffect(() => { resetAgentSteps() }, [])

    return {
        handleAnalyze,
        handleGenerate,
        handleStop,
        resetFlow: () => {
            store.setStage('input')
            store.setOptions([])
            store.setResult('')
            store.clearLogs()
            resetAgentSteps()
        }
    }
}
