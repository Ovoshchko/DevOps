import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { DetectionsPage } from '../pages/DetectionsPage'

const detectors = [
  { id: 'det-1', name: 'Detector A', status: 'active' },
]

const runs = [
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
]

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/detectors')) {
      return {
        ok: true,
        status: 200,
        json: async () => detectors,
      } as Response
    }
    if (url.includes('/detections')) {
      return {
        ok: true,
        status: 200,
        json: async () => runs,
      } as Response
    }
    return {
      ok: true,
      status: 200,
      json: async () => [],
    } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('renders detections title', async () => {
  render(<DetectionsPage />)
  await waitFor(() => expect(screen.getByText('Detections')).toBeInTheDocument())
})

test('renders score values and fallback in detections table', async () => {
  render(<DetectionsPage />)

  await waitFor(() => expect(screen.getByText('0.91')).toBeInTheDocument())
  expect(screen.getByText('Score')).toBeInTheDocument()
  expect(screen.getByText('true')).toBeInTheDocument()
  expect(screen.getByText('false')).toBeInTheDocument()

  const fallbackCells = screen.getAllByText('-')
  expect(fallbackCells.length).toBeGreaterThan(0)
})

test('keeps existing detection columns while adding score', async () => {
  render(<DetectionsPage />)

  await waitFor(() => expect(screen.getByRole('columnheader', { name: 'Detector' })).toBeInTheDocument())
  expect(screen.getByRole('columnheader', { name: 'Status' })).toBeInTheDocument()
  expect(screen.getByRole('columnheader', { name: 'Window' })).toBeInTheDocument()
  expect(screen.getByRole('columnheader', { name: 'Threshold' })).toBeInTheDocument()
  expect(screen.getByRole('columnheader', { name: 'Features' })).toBeInTheDocument()
  expect(screen.getByRole('columnheader', { name: 'Anomaly' })).toBeInTheDocument()
  expect(screen.getByRole('columnheader', { name: 'Score' })).toBeInTheDocument()
})
