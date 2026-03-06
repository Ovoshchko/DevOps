import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'

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
    return { ok: true, status: 200, json: async () => ({}) } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('monitoring page exposes detector profile filter input', () => {
  render(<MonitoringPage />)
  const input = screen.getByPlaceholderText('optional detector id')
  fireEvent.change(input, { target: { value: 'abc' } })
  expect((input as HTMLInputElement).value).toBe('abc')
})
