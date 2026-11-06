import type { Job } from '../api/client'

interface Props {
  jobs: Job[]
  selectedId: string | null
  onSelect: (id: string) => void
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString()
  } catch {
    return iso
  }
}

export function JobTable({ jobs, selectedId, onSelect }: Props) {
  return (
    <div className="panel">
      <h2>Jobs</h2>
      {jobs.length === 0 ? (
        <p className="muted">No jobs yet — submit one above.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Pri</th>
                <th>Attempts</th>
                <th>Created</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr
                  key={job.id}
                  className={job.id === selectedId ? 'selected' : undefined}
                  onClick={() => onSelect(job.id)}
                >
                  <td className="mono">{job.id.slice(0, 8)}</td>
                  <td>{job.type}</td>
                  <td>
                    <span className={`badge badge-${job.status}`}>{job.status}</span>
                  </td>
                  <td>{job.priority}</td>
                  <td>
                    {job.attempts}/{job.max_attempts}
                  </td>
                  <td>{formatTime(job.created_at)}</td>
                  <td>{formatTime(job.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
