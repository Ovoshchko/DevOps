import React from 'react'
import { render, screen } from '@testing-library/react'
import { ErrorBanner } from '../components/ErrorBanner'

test('renders nothing when error is empty', () => {
  const { container } = render(<ErrorBanner />)
  expect(container.firstChild).toBeNull()
})

test('renders alert when error exists', () => {
  render(<ErrorBanner error="Backend unavailable" />)
  expect(screen.getByRole('alert')).toHaveTextContent('Backend unavailable')
})
