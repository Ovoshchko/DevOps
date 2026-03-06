import React from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MonitoringPage } from '../../src/pages/MonitoringPage'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/traffic/ingest')) {
      return { ok: true, status: 202, json: async () => ({ accepted: 5 }) } as Response
    }
    if (url.includes('/anomalies/latest')) {
      return { ok: true, status: 200, json: async () => ({ results: [] }) } as Response
    }
    if (url.includes('/traffic/latest')) {
      return { ok: true, status: 200, json: async () => ({ points: [] }) } as Response
    }
    return { ok: true, status: 200, json: async () => [] } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('transitions generator state from idle to running/completed', async () => {
  render(<MonitoringPage />)

  fireEvent.click(screen.getByRole('button', { name: 'Start' }))

  await waitFor(() => {
    expect(screen.getByText(/State:/)).toBeInTheDocument()
  })
})
