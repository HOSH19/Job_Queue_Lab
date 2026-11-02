export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled'
export type JobType = 'sleep' | 'http_fetch' | 'fail'

export interface Job {
  id: string
  type: JobType | string
  payload: Record<string, unknown>
  status: JobStatus
  result: Record<string, unknown> | null
  error: string | null
  attempts: number
  max_attempts: number
  created_at: string
  updated_at: string
}

export interface JobCreate {
  type: JobType
  payload: Record<string, unknown>
  max_attempts?: number
}

export interface Health {
  status: string
  redis: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = (await res.json()) as { detail?: string }
      if (body.detail) detail = body.detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export function createJob(body: JobCreate): Promise<Job> {
  return request<Job>('/jobs', { method: 'POST', body: JSON.stringify(body) })
}

export function listJobs(status?: JobStatus): Promise<Job[]> {
  const q = status ? `?status=${status}` : ''
  return request<Job[]>(`/jobs${q}`)
}

export function getJob(id: string): Promise<Job> {
  return request<Job>(`/jobs/${id}`)
}

export function cancelJob(id: string): Promise<Job> {
  return request<Job>(`/jobs/${id}/cancel`, { method: 'POST' })
}

export function getHealth(): Promise<Health> {
  return request<Health>('/health')
}
