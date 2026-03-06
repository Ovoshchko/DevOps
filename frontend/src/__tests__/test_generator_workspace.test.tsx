import React from 'react'
import { render, screen } from '@testing-library/react'

import { GeneratorPage } from '../pages/GeneratorPage'

beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation(async () => {
    return { ok: true, status: 202, json: async () => ({ accepted: 1 }) } as Response
  })
})

afterEach(() => {
  jest.restoreAllMocks()
})

test('generator workspace renders standalone page', () => {
  render(<GeneratorPage />)
  expect(screen.getByRole('heading', { level: 2, name: 'Traffic Generator' })).toBeInTheDocument()
})
