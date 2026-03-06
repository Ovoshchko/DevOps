import React from 'react'

export function StatusBanner({ label }: { label: string }) {
  return <div className="status-banner panel">{label}</div>
}
