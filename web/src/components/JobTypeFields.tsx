/** Type-specific payload inputs for the enqueue form. */

import type { JobType } from '../api/client'

interface Props {
  type: JobType
  seconds: number
  url: string
  message: string
  onSeconds: (n: number) => void
  onUrl: (s: string) => void
  onMessage: (s: string) => void
}

export function JobTypeFields({
  type,
  seconds,
  url,
  message,
  onSeconds,
  onUrl,
  onMessage,
}: Props) {
  if (type === 'sleep') {
    return (
      <label>
        Seconds (0–10)
        <input
          type="number"
          min={0}
          max={10}
          step={0.5}
          value={seconds}
          onChange={(e) => onSeconds(Number(e.target.value))}
        />
      </label>
    )
  }
  if (type === 'http_fetch') {
    return (
      <label>
        URL
        <input type="url" value={url} onChange={(e) => onUrl(e.target.value)} required />
      </label>
    )
  }
  return (
    <label>
      Error message
      <input type="text" value={message} onChange={(e) => onMessage(e.target.value)} />
    </label>
  )
}
