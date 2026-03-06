import { useMemo, useState } from 'react'
import {
  DEFAULT_GENERATOR_CONFIG,
  GeneratorRunState,
  TrafficGeneratorConfig,
} from '../types/generator'
import { TrafficGeneratorService } from '../services/trafficGeneratorService'

const createInitialState = (): GeneratorRunState => ({
  runId: `run-${Date.now()}`,
  state: 'idle',
  totalBatches: 0,
  sentBatches: 0,
  acceptedPoints: 0,
})

export function useTrafficGenerator(onDataSent?: () => Promise<void> | void) {
  const [config, setConfig] = useState<TrafficGeneratorConfig>(DEFAULT_GENERATOR_CONFIG)
  const [runState, setRunState] = useState<GeneratorRunState>(createInitialState)
  const [service, setService] = useState<TrafficGeneratorService | null>(null)

  const canStart = useMemo(() => runState.state !== 'running', [runState.state])

  const start = async () => {
    if (!canStart) return

    const nextService = new TrafficGeneratorService()
    setService(nextService)

    setRunState((current) => ({
      ...current,
      runId: `run-${Date.now()}`,
      state: 'running',
      sentBatches: 0,
      totalBatches: Math.max(1, Math.ceil((config.durationSeconds * 1000) / config.intervalMs)),
      acceptedPoints: 0,
      lastError: undefined,
      startedAt: new Date().toISOString(),
      completedAt: undefined,
    }))

    await nextService.run(config, {
      onProgress: (next) => {
        setRunState((current) => ({ ...current, ...next, state: 'running' }))
        if (onDataSent) void onDataSent()
      },
      onComplete: (next) => {
        setRunState((current) => ({ ...current, ...next, state: 'completed' }))
        if (onDataSent) void onDataSent()
      },
      onError: (message) => {
        setRunState((current) => ({
          ...current,
          state: 'failed',
          lastError: message,
          completedAt: new Date().toISOString(),
        }))
      },
    })
  }

  const stop = () => {
    if (service) {
      service.stop()
      setRunState((current) => ({ ...current, state: 'completed', completedAt: new Date().toISOString() }))
    }
  }

  const reset = () => {
    setRunState(createInitialState())
  }

  return {
    config,
    setConfig,
    runState,
    start,
    stop,
    reset,
    canStart,
  }
}
