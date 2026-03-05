import React, { useEffect, useState } from 'react'
import { detectorsApi } from '../services/detectorsApi'
import { DetectorForm } from '../components/DetectorForm'

export function DetectorsPage() {
  const [items, setItems] = useState<any[]>([])
  const reload = () => detectorsApi.list().then(setItems).catch(() => setItems([]))
  useEffect(() => { reload() }, [])
  return (
    <main>
      <h2>Detectors</h2>
      <DetectorForm onSubmit={(payload) => detectorsApi.create(payload).then(reload)} />
      <ul>{items.map((d) => <li key={d.id}>{d.name}</li>)}</ul>
    </main>
  )
}
