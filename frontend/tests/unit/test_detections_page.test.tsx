import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DetectionsPage } from '../../src/pages/DetectionsPage'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, status: 200, json: async () => [] } as any)))
})

describe('DetectionsPage', () => {
  it('renders detections title', () => {
    render(<DetectionsPage />)
    expect(screen.getByText('Detections')).toBeDefined()
  })
})
