import React from 'react'
import { render } from '@testing-library/react'

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

test('detectors workspace snapshot', () => {
  const { asFragment } = render(<DetectorsPage />)
  expect(asFragment()).toMatchSnapshot()
})

test('monitoring workspace snapshot', () => {
  const { asFragment } = render(<MonitoringPage />)
  expect(asFragment()).toMatchSnapshot()
})

test('generator workspace snapshot', () => {
  const { asFragment } = render(<GeneratorPage />)
  expect(asFragment()).toMatchSnapshot()
})

test('detections workspace snapshot', () => {
  const { asFragment } = render(<DetectionsPage />)
  expect(asFragment()).toMatchSnapshot()
})
