import React, { useState } from 'react'
import { AppPage, AppShell } from './components/AppShell'
import { DetectionsPage } from './pages/DetectionsPage'
import { DetectorsPage } from './pages/DetectorsPage'
import { GeneratorPage } from './pages/GeneratorPage'
import { MonitoringPage } from './pages/MonitoringPage'
import './styles/base.css'

export default function App() {
  const [page, setPage] = useState<AppPage>('detectors')

  return (
    <AppShell page={page} setPage={setPage}>
      {page === 'detectors' && <DetectorsPage />}
      {page === 'monitoring' && <MonitoringPage />}
      {page === 'detections' && <DetectionsPage />}
      {page === 'generator' && <GeneratorPage />}
    </AppShell>
  )
}
