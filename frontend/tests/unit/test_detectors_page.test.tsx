import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DetectorsPage } from '../../src/pages/DetectorsPage'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, status: 200, json: async () => [] } as any)))
})

describe('DetectorsPage', () => {
  it('renders detectors title', () => {
    render(<DetectorsPage />)
    expect(screen.getByText('Detectors')).toBeDefined()
  })
})
