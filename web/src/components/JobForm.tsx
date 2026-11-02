import { useMemo, useState, type FormEvent } from 'react'
import { createJob, type Job, type JobType } from '../api/client'

interface Props {
  onCreated: (job: Job) => void
}

const DEFAULTS: Record<JobType, Record<string, unknown>> = {
  sleep: { seconds: 2 },
  http_fetch: { url: 'https://httpbin.org/get' },
  fail: { message: 'intentional failure' },
}

export function JobForm({ onCreated }: Props) {
  const [type, setType] = useState<JobType>('sleep')
  const [seconds, setSeconds] = useState(2)
  const [url, setUrl] = useState('https://httpbin.org/get')
  const [message, setMessage] = useState('intentional failure')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const payload = useMemo(() => {
    if (type === 'sleep') return { seconds }
    if (type === 'http_fetch') return { url }
    return { message }
  }, [type, seconds, url, message])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const job = await createJob({ type, payload })
      onCreated(job)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'failed to create job')
    } finally {
      setSubmitting(false)
    }
  }

  function onTypeChange(next: JobType) {
    setType(next)
    const d = DEFAULTS[next]
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

      {type === 'sleep' && (
        <label>
          Seconds (0–10)
          <input
            type="number"
            min={0}
            max={10}
            step={0.5}
            value={seconds}
            onChange={(e) => setSeconds(Number(e.target.value))}
          />
        </label>
      )}

      {type === 'http_fetch' && (
        <label>
          URL
          <input type="url" value={url} onChange={(e) => setUrl(e.target.value)} required />
        </label>
      )}

      {type === 'fail' && (
        <label>
          Error message
          <input type="text" value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
      )}

      <pre className="payload-preview">{JSON.stringify(payload, null, 2)}</pre>

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Submitting…' : 'Submit'}
      </button>
    </form>
  )
}
