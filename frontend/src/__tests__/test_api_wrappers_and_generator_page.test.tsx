import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'

import { apiRequest } from '../services/apiClient'
import { detectionsApi } from '../services/detectionsApi'
import { detectorsApi } from '../services/detectorsApi'
import { generatorApi } from '../services/generatorApi'
import { monitoringApi } from '../services/monitoringApi'
import { GeneratorPage } from '../pages/GeneratorPage'
import { StatusBanner } from '../components/StatusBanner'

jest.mock('../services/apiClient', () => ({
  apiRequest: jest.fn(),
}))

const mockedApiRequest = apiRequest as jest.Mock

jest.mock('../hooks/useTrafficGenerator', () => ({
  useTrafficGenerator: () => ({
    config: {
      profileName: 'demo-profile',
      sourcePrefix: 'sim-sensor',
      batchSize: 10,
      intervalMs: 1000,
      durationSeconds: 10,
      bytesMin: 100,
      bytesMax: 900,
    },
    setConfig: jest.fn(),
    runState: { runId: 'run-1', state: 'idle', totalBatches: 0, sentBatches: 0, acceptedPoints: 0 },
    start: jest.fn(),
    stop: jest.fn(),
    reset: jest.fn(),
    canStart: true,
  }),
}))

describe('api wrappers', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  test('detectionsApi builds the expected requests', () => {
    detectionsApi.run({ detector_config_id: 'det-1' })
    detectionsApi.list('profile id')
    detectionsApi.get('run-1')
    detectionsApi.results('run-1')

    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      1,
      '/detections/run',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      2,
      '/detections?detector_profile_id=profile%20id',
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(3, '/detections/run-1')
    expect(mockedApiRequest).toHaveBeenNthCalledWith(4, '/detections/run-1/results')
  })

  test('detectorsApi builds CRUD requests', () => {
    detectorsApi.list()
    detectorsApi.create({
      name: 'detector',
      sensitivity: 0.5,
      window_size_seconds: 60,
      window_step_seconds: 30,
      features: ['bytes_per_sec'],
    })
    detectorsApi.update('det-1', { status: 'archived' })
    detectorsApi.remove('det-1')

    expect(mockedApiRequest).toHaveBeenNthCalledWith(1, '/detectors')
    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      2,
      '/detectors',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      3,
      '/detectors/det-1',
      expect.objectContaining({ method: 'PUT' }),
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(4, '/detectors/det-1', { method: 'DELETE' })
  })

  test('monitoringApi and generatorApi build expected requests', () => {
    monitoringApi.ingest([{ timestamp: 't', source_id: 's', metrics: { bytes_per_sec: 1, packets_per_sec: 1 } }])
    monitoringApi.latestTraffic()
    monitoringApi.latestAnomalies('detector id')
    generatorApi.create({ profile_name: 'p', batch_size: 1, interval_ms: 250, duration_seconds: 1 })
    generatorApi.get('job-1')
    generatorApi.stop('job-1')

    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      1,
      '/traffic/ingest',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(2, '/traffic/latest')
    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      3,
      '/anomalies/latest?detector_profile_id=detector%20id',
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      4,
      '/generator/jobs',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(mockedApiRequest).toHaveBeenNthCalledWith(5, '/generator/jobs/job-1')
    expect(mockedApiRequest).toHaveBeenNthCalledWith(
      6,
      '/generator/jobs/job-1/stop',
      expect.objectContaining({ method: 'POST' }),
    )
  })
})

describe('GeneratorPage and StatusBanner', () => {
  test('renders generator workspace and status banner', () => {
    render(
      <>
        <GeneratorPage />
        <StatusBanner label="Ready" />
      </>,
    )

    expect(screen.getByRole('heading', { level: 2, name: 'Traffic Generator' })).toBeInTheDocument()
    expect(screen.getByText('Generator Status')).toBeInTheDocument()
    expect(screen.getByText('Ready')).toBeInTheDocument()
  })

  test('generator page exposes form actions from hook state', () => {
    render(<GeneratorPage />)

    expect(screen.getByRole('button', { name: 'Start' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    fireEvent.click(screen.getByRole('button', { name: 'Stop' }))
  })
})
