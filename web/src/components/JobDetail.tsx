/** Selected-job inspector with cancel for queued rows. */

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
    setBusy(true)
    setError(null)
    try {
      onUpdated(await cancelJob(job!.id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'cancel failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="panel">
      <DetailHeader job={job} busy={busy} onCancel={onCancel} />
      <DetailMeta job={job} />
      <Timeline job={job} />
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

function DetailHeader({
  job,
  busy,
  onCancel,
}: {
  job: Job
  busy: boolean
  onCancel: () => void
}) {
  return (
    <div className="detail-header">
      <h2>Detail</h2>
      {job.status === 'queued' && (
        <button type="button" className="danger" onClick={onCancel} disabled={busy}>
          {busy ? 'Cancelling…' : 'Cancel'}
        </button>
      )}
    </div>
  )
}

function DetailMeta({ job }: { job: Job }) {
  return (
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
      <dt>Priority</dt>
      <dd>{job.priority}</dd>
      <dt>Run at</dt>
      <dd>{job.run_at ? new Date(job.run_at).toLocaleString() : 'immediate'}</dd>
      <dt>Idempotency</dt>
      <dd className="mono">{job.idempotency_key ?? '—'}</dd>
    </dl>
  )
}

function Timeline({ job }: { job: Job }) {
  const attemptLabel = `${job.attempts}/${job.max_attempts}`
  return (
    <>
      <h3>Attempt timeline</h3>
      <ul className="timeline">
        <li>created {new Date(job.created_at).toLocaleString()}</li>
        <li>
          attempt {attemptLabel} · last update {new Date(job.updated_at).toLocaleString()}
        </li>
        {job.error && <li className="error">last error: {job.error}</li>}
        {job.status === 'succeeded' && <li>finished successfully</li>}
        {job.status === 'dead' && <li className="error">moved to dead-letter queue</li>}
      </ul>
    </>
  )
}
