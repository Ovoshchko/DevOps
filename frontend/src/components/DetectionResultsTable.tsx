import React from 'react'

export function DetectionResultsTable({ results }: { results: any[] }) {
  return (
    <section className="panel">
      <h3>Detection runs</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Status</th>
            <th>Window Start</th>
            <th>Window End</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.status}</td>
              <td>{r.window_start}</td>
              <td>{r.window_end}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
