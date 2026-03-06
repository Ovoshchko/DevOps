import React from 'react'
import { render, screen } from '@testing-library/react'
import { TrafficGeneratorStatus } from '../../src/components/TrafficGeneratorStatus'

test('shows status headline and progress details', () => {
  render(
    <TrafficGeneratorStatus
      runState={{
        runId: 'run-1',
        state: 'running',
        totalBatches: 10,
        sentBatches: 3,
        acceptedPoints: 30,
      }}
      onStop={jest.fn()}
      onRetry={jest.fn()}
    />, 
  )

  expect(screen.getByText('Generator Status')).toBeInTheDocument()
  expect(screen.getByText('Progress: 3/10 batches')).toBeInTheDocument()
})
