/** Job and health HTTP helpers. */

import { request } from './request'
import type { Health, Job, JobCreate, JobStatus } from './types'

/** POST /jobs, optionally with Idempotency-Key. */
export function createJob(body: JobCreate, idempotencyKey?: string): Promise<Job> {
  return request<Job>('/jobs', {
    method: 'POST',
    body: JSON.stringify(body),
    ...(idempotencyKey ? { headers: { 'Idempotency-Key': idempotencyKey } } : {}),
  })
}

/** GET /jobs with optional status filter. */
export function listJobs(status?: JobStatus): Promise<Job[]> {
  const q = status ? `?status=${status}` : ''
  return request<Job[]>(`/jobs${q}`)
}

/** GET /jobs/{id}. */
export function getJob(id: string): Promise<Job> {
  return request<Job>(`/jobs/${id}`)
}

/** POST /jobs/{id}/cancel. */
export function cancelJob(id: string): Promise<Job> {
  return request<Job>(`/jobs/${id}/cancel`, { method: 'POST' })
}

/** GET /health. */
export function getHealth(): Promise<Health> {
  return request<Health>('/health')
}

/** GET /dlq. */
export function listDlq(): Promise<{ job_id: string }[]> {
  return request<{ job_id: string }[]>('/dlq')
}

/**
 * WebSocket URL for live events.
 * Dev connects to FastAPI directly to avoid Vite WS proxy issues.
 */
export function jobsWebSocketUrl(): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  if (import.meta.env.DEV) {
    return `${proto}://127.0.0.1:8000/ws/jobs`
  }
  return `${proto}://${window.location.host}/ws/jobs`
}
