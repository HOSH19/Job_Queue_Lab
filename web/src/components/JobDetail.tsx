import { useState } from 'react'
import { cancelJob, type Job } from '../api/client'

interface Props {
  job: Job | null
  onUpdated: (job: Job) => void
}

export function JobDetail({ job, onUpdated }: Props) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!job) {
    return (
      <div className="panel">
        <h2>Detail</h2>
        <p className="muted">Select a job to inspect result / error.</p>
      </div>
    )
  }

  async function onCancel() {
    if (!job) return
    setBusy(true)
    setError(null)
    try {
      const updated = await cancelJob(job.id)
      onUpdated(updated)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'cancel failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="panel">
      <div className="detail-header">
        <h2>Detail</h2>
        {job.status === 'queued' && (
          <button type="button" className="danger" onClick={onCancel} disabled={busy}>
            {busy ? 'Cancelling…' : 'Cancel'}
          </button>
        )}
      </div>
      <dl className="detail-grid">
        <dt>ID</dt>
        <dd className="mono">{job.id}</dd>
        <dt>Type</dt>
        <dd>{job.type}</dd>
        <dt>Status</dt>
        <dd>
          <span className={`badge badge-${job.status}`}>{job.status}</span>
        </dd>
        <dt>Attempts</dt>
        <dd>
          {job.attempts}/{job.max_attempts}
        </dd>
      </dl>

      <h3>Payload</h3>
      <pre>{JSON.stringify(job.payload, null, 2)}</pre>

      {job.result && (
        <>
          <h3>Result</h3>
          <pre>{JSON.stringify(job.result, null, 2)}</pre>
        </>
      )}

      {job.error && (
        <>
          <h3>Error</h3>
          <pre className="error-block">{job.error}</pre>
        </>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  )
}
