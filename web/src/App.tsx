import { useCallback, useEffect, useMemo, useState } from 'react'
import { getHealth, listJobs, type Health, type Job } from './api/client'
import { JobDetail } from './components/JobDetail'
import { JobForm } from './components/JobForm'
import { JobTable } from './components/JobTable'
import './App.css'

function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [health, setHealth] = useState<Health | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  const selected = useMemo(
    () => jobs.find((j) => j.id === selectedId) ?? null,
    [jobs, selectedId],
  )

  const refresh = useCallback(async () => {
    try {
      const [nextJobs, nextHealth] = await Promise.all([listJobs(), getHealth()])
      setJobs(nextJobs)
      setHealth(nextHealth)
      setLoadError(null)
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'failed to load jobs')
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const hasActive = jobs.some((j) => j.status === 'queued' || j.status === 'running')

  useEffect(() => {
    if (!hasActive) return
    const id = window.setInterval(() => {
      void refresh()
    }, 1000)
    return () => window.clearInterval(id)
  }, [hasActive, refresh])

  function onCreated(job: Job) {
    setJobs((prev) => [job, ...prev.filter((j) => j.id !== job.id)])
    setSelectedId(job.id)
  }

  function onUpdated(job: Job) {
    setJobs((prev) => prev.map((j) => (j.id === job.id ? job : j)))
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">Job Queue Lab</p>
          <h1>Enqueue → Redis → Worker → Status</h1>
        </div>
        <div className="health">
          {health ? (
            <>
              <span className={`dot ${health.redis === 'up' ? 'ok' : 'bad'}`} />
              API {health.status} · Redis {health.redis}
            </>
          ) : (
            <span className="muted">Checking health…</span>
          )}
        </div>
      </header>

      {loadError && <p className="error banner">{loadError} — is the API running on :8000?</p>}

      <div className="layout">
        <JobForm onCreated={onCreated} />
        <JobTable jobs={jobs} selectedId={selectedId} onSelect={setSelectedId} />
        <JobDetail job={selected} onUpdated={onUpdated} />
      </div>
    </div>
  )
}

export default App
