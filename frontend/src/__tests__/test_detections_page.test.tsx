import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { DetectionsPage } from '../pages/DetectionsPage'

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

test('renders detections title', async () => {
  render(<DetectionsPage />)
  await waitFor(() => expect(screen.getByText('Detections')).toBeInTheDocument())
})
