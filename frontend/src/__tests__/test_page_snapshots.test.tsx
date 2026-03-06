import React from 'react'
import { render } from '@testing-library/react'
import { DetectorsPage } from '../pages/DetectorsPage'
import { MonitoringPage } from '../pages/MonitoringPage'
import { DetectionsPage } from '../pages/DetectionsPage'

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

test('detectors page snapshot', () => {
  const { asFragment } = render(<DetectorsPage />)
  expect(asFragment()).toMatchSnapshot()
})

test('monitoring page snapshot', () => {
  const { asFragment } = render(<MonitoringPage />)
  expect(asFragment()).toMatchSnapshot()
})

test('detections page snapshot', () => {
  const { asFragment } = render(<DetectionsPage />)
  expect(asFragment()).toMatchSnapshot()
})
