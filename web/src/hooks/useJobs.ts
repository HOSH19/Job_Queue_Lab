/** Load and cache the job list plus API health. */

import { useCallback, useEffect, useMemo, useState } from 'react'
import { getHealth, listJobs, type Health, type Job } from '../api/client'

export function useJobs() {
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

  function onCreated(job: Job) {
    setJobs((prev) => [job, ...prev.filter((j) => j.id !== job.id)])
    setSelectedId(job.id)
  }

  function onUpdated(job: Job) {
    setJobs((prev) => prev.map((j) => (j.id === job.id ? job : j)))
  }

  return {
    jobs,
    selected,
    selectedId,
    setSelectedId,
    health,
    loadError,
    refresh,
    onCreated,
    onUpdated,
  }
}
