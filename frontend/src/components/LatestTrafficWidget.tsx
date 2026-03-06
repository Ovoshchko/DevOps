import React from 'react'

export function LatestTrafficWidget({ points }: { points: any[] }) {
  const recent = points.slice(0, 8)
  const bytesSeries = recent.map((point) => Number(point.metrics?.bytes_per_sec ?? 0))
  const maxBytes = Math.max(...bytesSeries, 1)
  const avgBytes =
    recent.length > 0 ? Math.round(bytesSeries.reduce((acc, value) => acc + value, 0) / recent.length) : 0
  const chartPoints = recent
    .map((point, index) => {
      const x = recent.length === 1 ? 0 : Math.round((index / (recent.length - 1)) * 100)
      const y = 100 - Math.round((Number(point.metrics?.bytes_per_sec ?? 0) / maxBytes) * 100)
      return `${x},${Math.min(100, Math.max(0, y))}`
    })
    .join(' ')

  return (
    <section className="panel">
      <h3>Latest Traffic</h3>
      <p className="small">
        Points received: {points.length}. Avg throughput (last {recent.length || 0}): {avgBytes} bytes/sec
      </p>
      {recent.length > 0 ? (
        <div className="traffic-rows">
          <div className="traffic-chart">
            <p className="small">Traffic trend (bytes/sec)</p>
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Traffic throughput trend">
              <polyline points={chartPoints} />
            </svg>
          </div>
          {recent.map((point) => {
            const bytesPerSec = Number(point.metrics?.bytes_per_sec ?? 0)
            const ratio = Math.max(4, Math.round((bytesPerSec / maxBytes) * 100))
            const packetsPerSec = point.metrics?.packets_per_sec ?? 'n/a'
            const latencyMs = point.metrics?.latency_ms ?? 'n/a'
            const timeValue = point.timestamp ? new Date(point.timestamp).toLocaleTimeString() : 'n/a'

            return (
              <div className="traffic-row" key={point.id ?? `${point.source_id}-${point.timestamp}`}>
                <div className="traffic-row-header">
                  <strong>{point.source_id}</strong>
                  <span className="small">{timeValue}</span>
                </div>
                <div className="traffic-bar-wrap" aria-hidden="true">
                  <div className="traffic-bar" style={{ width: `${ratio}%` }} />
                </div>
                <p className="small">
                  {bytesPerSec} bytes/sec, {packetsPerSec} packets/sec, latency {latencyMs} ms
                </p>
              </div>
            )
          })}
        </div>
      ) : (
        <p className="small">No traffic yet.</p>
      )}
    </section>
  )
}
