/** Shared API types for the job queue UI. */

export type JobStatus =
  | 'queued'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'cancelled'
  | 'dead'

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
  priority: number
  run_at: string | null
  idempotency_key: string | null
  created_at: string
  updated_at: string
}

export interface JobCreate {
  type: JobType
  payload: Record<string, unknown>
  max_attempts?: number
  priority?: number
  run_at?: string | null
}

export interface Health {
  status: string
  redis: string
  database: string
}
