import React from 'react'
import { render, screen } from '@testing-library/react'

import { DetectionsPage } from '../pages/DetectionsPage'
import { DetectorsPage } from '../pages/DetectorsPage'
import { GeneratorPage } from '../pages/GeneratorPage'
import { MonitoringPage } from '../pages/MonitoringPage'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/anomalies/latest')) return { ok: true, status: 200, json: async () => ({ results: [] }) } as Response
    if (url.includes('/traffic/latest')) return { ok: true, status: 200, json: async () => ({ points: [] }) } as Response
    if (url.includes('/detections')) return { ok: true, status: 200, json: async () => [] } as Response
    if (url.includes('/detectors')) return { ok: true, status: 200, json: async () => [] } as Response
    return { ok: true, status: 200, json: async () => ({}) } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('detectors workspace snapshot', async () => {
  const { asFragment } = render(<DetectorsPage />)
  await screen.findByRole('heading', { name: 'Detectors' })
  expect(asFragment()).toMatchSnapshot()
})

test('monitoring workspace snapshot', async () => {
  const { asFragment } = render(<MonitoringPage />)
  await screen.findByRole('heading', { name: 'Monitoring' })
  expect(asFragment()).toMatchSnapshot()
})

test('generator workspace snapshot', async () => {
  const { asFragment } = render(<GeneratorPage />)
  await screen.findByRole('button', { name: 'Start' })
  expect(asFragment()).toMatchSnapshot()
})

test('detections workspace snapshot', async () => {
  const { asFragment } = render(<DetectionsPage />)
  await screen.findByRole('heading', { name: 'Detections' })
  await screen.findByText(/Active detector:/)
  expect(asFragment()).toMatchSnapshot()
})
