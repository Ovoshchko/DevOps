import React from 'react'

export function LatestAnomaliesWidget({ results }: { results: any[] }) {
  return <section><h3>Latest Anomalies</h3><div>{results.length} anomalies</div></section>
}
