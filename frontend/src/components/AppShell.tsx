import React from 'react'

export type AppPage = 'detectors' | 'monitoring' | 'detections' | 'generator'

type Props = {
  page: AppPage
  setPage: (p: AppPage) => void
  children: React.ReactNode
}

const PAGES: { key: AppPage; label: string }[] = [
  { key: 'detectors', label: 'Detectors' },
  { key: 'monitoring', label: 'Monitoring' },
  { key: 'detections', label: 'Detections' },
  { key: 'generator', label: 'Traffic Generator' },
]

export function AppShell({ page, setPage, children }: Props) {
  return (
    <div className="app-shell">
      <header className="top-nav">
        <div>
          <p className="small">Network Operations</p>
          <h1>Traffic Anomaly Platform</h1>
        </div>
        <nav aria-label="Main navigation">
          {PAGES.map((entry) => (
            <button
              key={entry.key}
              className={page === entry.key ? 'primary' : ''}
              onClick={() => setPage(entry.key)}
              aria-current={page === entry.key ? 'page' : undefined}
              type="button"
            >
              {entry.label}
            </button>
          ))}
        </nav>
      </header>
      <section className="content">{children}</section>
    </div>
  )
}
