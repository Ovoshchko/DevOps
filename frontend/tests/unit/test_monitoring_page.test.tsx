import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MonitoringPage } from '../../src/pages/MonitoringPage'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    if (url.includes('/anomalies/latest')) return { ok: true, status: 200, json: async () => ({ results: [] }) } as any
    return { ok: true, status: 200, json: async () => ({ points: [] }) } as any
  }))
})

describe('MonitoringPage', () => {
  it('renders monitoring title', () => {
    render(<MonitoringPage />)
    expect(screen.getByText('Monitoring')).toBeDefined()
  })
})
