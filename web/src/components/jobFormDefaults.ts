/** Default payloads shown when switching job type in the form. */

import type { JobType } from '../api/client'

export const JOB_TYPE_DEFAULTS: Record<JobType, Record<string, unknown>> = {
  sleep: { seconds: 2 },
  http_fetch: { url: 'https://httpbin.org/get' },
  fail: { message: 'intentional failure' },
}

/** Build the JSON payload for the selected job type. */
export function buildPayload(
  type: JobType,
  fields: { seconds: number; url: string; message: string },
): Record<string, unknown> {
  if (type === 'sleep') return { seconds: fields.seconds }
  if (type === 'http_fetch') return { url: fields.url }
  return { message: fields.message }
}

/** ISO run_at from a relative delay, or null when delay is zero. */
export function runAtFromDelay(delaySeconds: number): string | null {
  if (delaySeconds <= 0) return null
  return new Date(Date.now() + delaySeconds * 1000).toISOString()
}
