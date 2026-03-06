export type GeneratorState = 'idle' | 'running' | 'completed' | 'failed'

export type TrafficGeneratorConfig = {
  profileName: string
  sourcePrefix: string
  batchSize: number
  intervalMs: number
  durationSeconds: number
  bytesMin: number
  bytesMax: number
}

export type GeneratorRunState = {
  runId: string
  state: GeneratorState
  totalBatches: number
  sentBatches: number
  acceptedPoints: number
  lastError?: string
  startedAt?: string
  completedAt?: string
}

export type TrafficPoint = {
  timestamp: string
  source_id: string
  metrics: {
    bytes_per_sec: number
    packets_per_sec: number
  }
  tags?: Record<string, string>
}

export const DEFAULT_GENERATOR_CONFIG: TrafficGeneratorConfig = {
  profileName: 'demo-profile',
  sourcePrefix: 'sim-sensor',
  batchSize: 10,
  intervalMs: 1000,
  durationSeconds: 10,
  bytesMin: 100,
  bytesMax: 900,
}
