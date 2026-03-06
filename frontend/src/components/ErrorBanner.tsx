import React from 'react'

export function ErrorBanner({ error }: { error?: string }) {
  if (!error) return null
  return (
    <div className="error-banner panel" role="alert" aria-live="polite">
      <strong>Error:</strong> {error}
    </div>
  )
}
