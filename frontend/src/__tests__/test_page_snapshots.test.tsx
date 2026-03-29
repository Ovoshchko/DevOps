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
    if (url.includes('/detectors')) {
      return {
        ok: true,
        status: 200,
        json: async () => [{ id: 'det-1', name: 'Detector A', status: 'active' }],
      } as Response
    }
    if (url.includes('/detections')) {
      return {
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 'run-1',
            detector_config_id: 'det-1',
            status: 'completed',
            window_start: '2026-03-29T10:00:00Z',
            window_end: '2026-03-29T10:05:00Z',
            summary: {
              threshold: 0.7,
              features: ['bytes_per_sec'],
              anomaly_score: 0.91,
              is_anomaly: true,
            },
          },
          {
            id: 'run-2',
            detector_config_id: 'det-1',
            status: 'completed',
            window_start: '2026-03-29T10:05:00Z',
            window_end: '2026-03-29T10:10:00Z',
            summary: {
              threshold: 0.7,
              features: ['packets_per_sec'],
              is_anomaly: false,
            },
          },
        ],
      } as Response
    }
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
