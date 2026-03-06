import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { MonitoringPage } from '../pages/MonitoringPage'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/anomalies/latest')) {
      return { ok: true, status: 200, json: async () => ({ results: [] }) } as Response
    }
    if (url.includes('/traffic/latest')) {
      return { ok: true, status: 200, json: async () => ({ points: [] }) } as Response
    }
    return { ok: true, status: 202, json: async () => ({ accepted: 10 }) } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('renders monitoring title', async () => {
  render(<MonitoringPage />)
  await waitFor(() => expect(screen.getByText('Monitoring')).toBeInTheDocument())
  expect(screen.getByText(/Points received:/)).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Refresh now' })).toBeInTheDocument()
})
