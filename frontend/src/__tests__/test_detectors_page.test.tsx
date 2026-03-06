import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { DetectorsPage } from '../pages/DetectorsPage'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async () => {
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

test('renders detectors title', async () => {
  render(<DetectorsPage />)
  await waitFor(() => expect(screen.getByText('Detectors')).toBeInTheDocument())
})
