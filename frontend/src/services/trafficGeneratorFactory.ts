import { TrafficGeneratorConfig, TrafficPoint } from '../types/generator'

function randomInRange(min: number, max: number): number {
  const low = Math.min(min, max)
  const high = Math.max(min, max)
  return Math.round(low + Math.random() * (high - low))
}

export function createTrafficBatch(config: TrafficGeneratorConfig): TrafficPoint[] {
  const now = new Date()

  return Array.from({ length: config.batchSize }).map((_, index) => {
    const sourceNumber = (index % Math.max(1, Math.floor(config.batchSize / 2))) + 1
    const bytesPerSecond = randomInRange(config.bytesMin, config.bytesMax)

    return {
      timestamp: new Date(now.getTime() - index * 250).toISOString(),
      source_id: `${config.sourcePrefix}-${sourceNumber}`,
      metrics: {
        bytes_per_sec: bytesPerSecond,
        packets_per_sec: Math.max(1, Math.round(bytesPerSecond / 12)),
      },
      tags: {
        profile: config.profileName,
        mode: 'synthetic',
      },
    }
  })
}
