import React from 'react'

export function LatestTrafficWidget({ points }: { points: any[] }) {
  return <section><h3>Latest Traffic</h3><div>{points.length} points</div></section>
}
