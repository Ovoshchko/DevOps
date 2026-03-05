import React, { useState } from 'react'

export function DetectorForm({ onSubmit }: { onSubmit: (v: any) => void }) {
  const [name, setName] = useState('Default detector')
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit({ name, sensitivity: 0.7, window_size_seconds: 60, window_step_seconds: 30, features: ['bytes_per_sec'] }) }}>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <button type="submit">Save detector</button>
    </form>
  )
}
