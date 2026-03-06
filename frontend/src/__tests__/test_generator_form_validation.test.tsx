import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { TrafficGeneratorForm } from '../components/TrafficGeneratorForm'
import { DEFAULT_GENERATOR_CONFIG } from '../types/generator'

test('shows validation error when batch size is invalid', () => {
  const onStart = jest.fn()
  const onChange = jest.fn()
  render(
    <TrafficGeneratorForm
      config={{ ...DEFAULT_GENERATOR_CONFIG, batchSize: 0 }}
      onStart={onStart}
      onChange={onChange}
      disabled={false}
    />,
  )

  fireEvent.click(screen.getByRole('button', { name: 'Start' }))
  expect(screen.getByText('Batch size must be greater than 0')).toBeInTheDocument()
  expect(onStart).not.toHaveBeenCalled()
})
