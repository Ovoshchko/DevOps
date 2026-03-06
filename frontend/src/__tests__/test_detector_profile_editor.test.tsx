import React from 'react'
import { render, screen } from '@testing-library/react'

import { DetectorForm } from '../components/DetectorForm'


test('detector profile editor renders base controls', () => {
  render(<DetectorForm onSubmit={jest.fn()} />)
  expect(screen.getByText('Create detector')).toBeInTheDocument()
  expect(screen.getByLabelText('Sensitivity (0.1 - 1.0)')).toBeInTheDocument()
  expect(screen.getByLabelText('Window size (seconds)')).toBeInTheDocument()
  expect(screen.getByLabelText('Features (comma-separated)')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Save detector' })).toBeInTheDocument()
})
