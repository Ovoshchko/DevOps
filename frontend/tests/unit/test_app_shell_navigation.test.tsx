import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import App from '../../src/App'

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

test('switches between app sections from top navigation', () => {
  render(<App />)

  expect(screen.getByText('Detectors')).toBeInTheDocument()

  fireEvent.click(screen.getByRole('button', { name: 'Monitoring' }))
  expect(screen.getByText('Monitoring')).toBeInTheDocument()

  fireEvent.click(screen.getByRole('button', { name: 'Detections' }))
  expect(screen.getByText('Detections')).toBeInTheDocument()
})
