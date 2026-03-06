import React from 'react'
import { render, screen } from '@testing-library/react'
import { AppShell } from '../../src/components/AppShell'

test('renders responsive shell elements', () => {
  render(
    <AppShell page="monitoring" setPage={jest.fn()}>
      <div>Content</div>
    </AppShell>,
  )

  expect(screen.getByRole('navigation', { name: 'Main navigation' })).toBeInTheDocument()
  expect(screen.getByText('Traffic Anomaly Platform')).toBeInTheDocument()
})
