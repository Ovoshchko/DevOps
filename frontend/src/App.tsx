import React, { useState } from 'react'
import { DetectorsPage } from './pages/DetectorsPage'
import { MonitoringPage } from './pages/MonitoringPage'
import { DetectionsPage } from './pages/DetectionsPage'

export default function App() {
  const [page, setPage] = useState<'detectors'|'monitoring'|'detections'>('detectors')
  return (
    <div>
      <nav>
        <button onClick={() => setPage('detectors')}>Detectors</button>
        <button onClick={() => setPage('monitoring')}>Monitoring</button>
        <button onClick={() => setPage('detections')}>Detections</button>
      </nav>
      {page === 'detectors' && <DetectorsPage />}
      {page === 'monitoring' && <MonitoringPage />}
      {page === 'detections' && <DetectionsPage />}
    </div>
  )
}
