import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'

import { DetectorsPage } from '../pages/DetectorsPage'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async () => {
    return {
      ok: true,
      status: 200,
      json: async () => [
        {
          id: 'persisted-1',
          name: 'Persisted Profile',
          status: 'active',
          sensitivity: 0.7,
          window_size_seconds: 60,
          window_step_seconds: 30,
          features: ['bytes_per_sec'],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
    } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('detector list can render persisted records after load', async () => {
  render(<DetectorsPage />)
  await waitFor(() => expect(screen.getByText(/Persisted Profile/)).toBeInTheDocument())
})
