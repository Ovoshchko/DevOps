import React from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from '../App'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/anomalies/latest')) return { ok: true, status: 200, json: async () => ({ results: [] }) } as Response
    if (url.includes('/traffic/latest')) return { ok: true, status: 200, json: async () => ({ points: [] }) } as Response
    return { ok: true, status: 200, json: async () => [] } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('switches between app sections from top navigation', async () => {
  render(<App />)

  await waitFor(() => expect(screen.getByRole('heading', { name: 'Detectors' })).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: 'Monitoring' }))
  expect(screen.getByRole('heading', { name: 'Monitoring' })).toBeInTheDocument()

  fireEvent.click(screen.getByRole('button', { name: 'Detections' }))
  expect(screen.getByRole('heading', { name: 'Detections' })).toBeInTheDocument()
})
