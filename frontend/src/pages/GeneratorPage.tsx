import React from 'react'

import { TrafficGeneratorForm } from '../components/TrafficGeneratorForm'
import { TrafficGeneratorStatus } from '../components/TrafficGeneratorStatus'
import { useTrafficGenerator } from '../hooks/useTrafficGenerator'

export function GeneratorPage() {
  const generator = useTrafficGenerator()

  return (
    <main>
      <h2>Traffic Generator</h2>
      <p className="small">Run synthetic traffic generation in a dedicated workspace.</p>
      <section className="page-grid-two">
        <TrafficGeneratorForm
          config={generator.config}
          onChange={generator.setConfig}
          onStart={() => void generator.start()}
          disabled={!generator.canStart}
        />
        <TrafficGeneratorStatus
          runState={generator.runState}
          onStop={generator.stop}
          onRetry={() => {
            generator.reset()
            void generator.start()
          }}
        />
      </section>
    </main>
  )
}
