import { monitoringApi } from './monitoringApi'
import { createTrafficBatch } from './trafficGeneratorFactory'
import { GeneratorRunState, TrafficGeneratorConfig } from '../types/generator'

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms))

type Handlers = {
  onProgress: (next: Partial<GeneratorRunState>) => void
  onComplete: (next: Partial<GeneratorRunState>) => void
  onError: (message: string) => void
}

export class TrafficGeneratorService {
  private stopped = false

  stop(): void {
    this.stopped = true
  }

  async run(config: TrafficGeneratorConfig, handlers: Handlers): Promise<void> {
    this.stopped = false

    const totalBatches = Math.max(1, Math.ceil((config.durationSeconds * 1000) / config.intervalMs))
    for (let sent = 1; sent <= totalBatches; sent += 1) {
      if (this.stopped) {
        handlers.onComplete({ state: 'completed', completedAt: new Date().toISOString() })
        return
      }

      try {
        const points = createTrafficBatch(config)
        const response = await monitoringApi.ingest(points)

        handlers.onProgress({
          sentBatches: sent,
          totalBatches,
          acceptedPoints: Math.max(0, response.accepted),
        })
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to send generated traffic'
        handlers.onError(message)
        return
      }

      if (sent < totalBatches) {
        await sleep(config.intervalMs)
      }
    }

    handlers.onComplete({
      state: 'completed',
      totalBatches,
      sentBatches: totalBatches,
      completedAt: new Date().toISOString(),
    })
  }
}
