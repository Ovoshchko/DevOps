import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'

import { DetectionRunForm } from '../components/DetectionRunForm'
import { DetectorForm } from '../components/DetectorForm'
import { LatestTrafficWidget } from '../components/LatestTrafficWidget'

describe('DetectorForm', () => {
  test('submits trimmed features and selected status', () => {
    const onSubmit = jest.fn()
    render(<DetectorForm onSubmit={onSubmit} />)

    fireEvent.change(screen.getByLabelText('Detector name'), { target: { value: 'Primary detector' } })
    fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'draft' } })
    fireEvent.change(screen.getByLabelText('Features (comma-separated)'), {
      target: { value: ' bytes_per_sec , packets_per_sec ,  ' },
    })
    fireEvent.submit(screen.getByRole('button', { name: 'Save detector' }))

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Primary detector',
        status: 'draft',
        features: ['bytes_per_sec', 'packets_per_sec'],
      }),
    )
  })

  test('falls back to bytes_per_sec when features input is blank', () => {
    const onSubmit = jest.fn()
    render(<DetectorForm onSubmit={onSubmit} />)

    fireEvent.change(screen.getByLabelText('Features (comma-separated)'), {
      target: { value: ' ,   , ' },
    })
    fireEvent.submit(screen.getByRole('button', { name: 'Save detector' }))

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        features: ['bytes_per_sec'],
      }),
    )
  })
})

describe('LatestTrafficWidget', () => {
  test('renders empty state when there is no traffic', () => {
    render(<LatestTrafficWidget points={[]} />)

    expect(screen.getByText('No traffic yet.')).toBeInTheDocument()
    expect(screen.getByText('Points received: 0. Avg throughput (last 0): 0 bytes/sec')).toBeInTheDocument()
  })

  test('renders chart summary and traffic rows for recent points', () => {
    render(
      <LatestTrafficWidget
        points={[
          {
            source_id: 'sensor-a',
            timestamp: '2026-04-02T10:00:00Z',
            metrics: { bytes_per_sec: 100, packets_per_sec: 10, latency_ms: 7 },
          },
          {
            source_id: 'sensor-b',
            timestamp: '2026-04-02T10:00:10Z',
            metrics: { bytes_per_sec: 200, packets_per_sec: 15, latency_ms: 9 },
          },
        ]}
      />,
    )

    expect(screen.getByLabelText('Traffic throughput trend')).toBeInTheDocument()
    expect(screen.getByText(/Avg throughput \(last 2\): 150 bytes\/sec/)).toBeInTheDocument()
    expect(screen.getByText('sensor-a')).toBeInTheDocument()
    expect(screen.getByText('sensor-b')).toBeInTheDocument()
  })
})

describe('DetectionRunForm', () => {
  test('disables detector selection and run action when no detectors exist', () => {
    const onRun = jest.fn()
    render(
      <DetectionRunForm
        detectors={[]}
        selectedDetectorId=""
        onChangeDetector={jest.fn()}
        onRun={onRun}
      />,
    )

    expect(screen.getByDisplayValue('No detectors available')).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Run detection' })).toBeDisabled()
  })

  test('submits a detection payload for the selected detector', () => {
    const onRun = jest.fn()
    const onChangeDetector = jest.fn()
    jest.useFakeTimers().setSystemTime(new Date('2026-04-02T10:00:00Z'))

    render(
      <DetectionRunForm
        detectors={[{ id: 'det-1', name: 'Detector A', status: 'active' }]}
        selectedDetectorId="det-1"
        onChangeDetector={onChangeDetector}
        onRun={onRun}
      />,
    )

    fireEvent.change(screen.getByDisplayValue('Detector A (active)'), { target: { value: 'det-1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Run detection' }))

    expect(onChangeDetector).toHaveBeenCalledWith('det-1')
    expect(onRun).toHaveBeenCalledWith({
      detector_config_id: 'det-1',
      window_start: '2026-04-02T09:59:00.000Z',
      window_end: '2026-04-02T10:00:00.000Z',
    })

    jest.useRealTimers()
  })
})
