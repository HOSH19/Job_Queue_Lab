/** Form to enqueue sleep / http_fetch / fail jobs. */

import { useMemo, useState, type FormEvent } from 'react'
import { createJob, type Job, type JobType } from '../api/client'
import { JobTypeFields } from './JobTypeFields'
import { JOB_TYPE_DEFAULTS, buildPayload, runAtFromDelay } from './jobFormDefaults'

interface Props {
  onCreated: (job: Job) => void
}

export function JobForm({ onCreated }: Props) {
  const [type, setType] = useState<JobType>('sleep')
  const [seconds, setSeconds] = useState(2)
  const [url, setUrl] = useState('https://httpbin.org/get')
  const [message, setMessage] = useState('intentional failure')
  const [priority, setPriority] = useState(0)
  const [delaySeconds, setDelaySeconds] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const payload = useMemo(
    () => buildPayload(type, { seconds, url, message }),
    [type, seconds, url, message],
  )

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const job = await createJob({
        type,
        payload,
        priority,
        run_at: runAtFromDelay(delaySeconds),
      })
      onCreated(job)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'failed to create job')
    } finally {
      setSubmitting(false)
    }
  }

  function onTypeChange(next: JobType) {
    setType(next)
    const d = JOB_TYPE_DEFAULTS[next]
    if (next === 'sleep') setSeconds(Number(d.seconds))
    if (next === 'http_fetch') setUrl(String(d.url))
    if (next === 'fail') setMessage(String(d.message))
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Enqueue job</h2>
      <label>
        Type
        <select value={type} onChange={(e) => onTypeChange(e.target.value as JobType)}>
          <option value="sleep">sleep</option>
          <option value="http_fetch">http_fetch</option>
          <option value="fail">fail</option>
        </select>
      </label>
      <JobTypeFields
        type={type}
        seconds={seconds}
        url={url}
        message={message}
        onSeconds={setSeconds}
        onUrl={setUrl}
        onMessage={setMessage}
      />
      <label>
        Priority (0–10)
        <input
          type="number"
          min={0}
          max={10}
          value={priority}
          onChange={(e) => setPriority(Number(e.target.value))}
        />
      </label>
      <label>
        Delay seconds (scheduled)
        <input
          type="number"
          min={0}
          max={3600}
          value={delaySeconds}
          onChange={(e) => setDelaySeconds(Number(e.target.value))}
        />
      </label>
      <pre className="payload-preview">
        {JSON.stringify({ ...payload, priority, delaySeconds }, null, 2)}
      </pre>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Submitting…' : 'Submit'}
      </button>
    </form>
  )
}
