/** Top bar: title plus live/polling and dependency health. */

import type { Health } from '../api/client'

interface Props {
  live: boolean
  health: Health | null
}

export function AppHeader({ live, health }: Props) {
  return (
    <header className="header">
      <div>
        <p className="eyebrow">Job Queue Lab</p>
        <h1>Enqueue → Redis → Worker → Status</h1>
      </div>
      <div className="health">
        <span className={`dot ${live ? 'ok' : 'bad'}`} title="live updates" />
        {live ? 'live' : 'polling'}
        {' · '}
        {health ? (
          <>
            API {health.status} · Redis {health.redis} · DB {health.database}
          </>
        ) : (
          <span className="muted">Checking health…</span>
        )}
      </div>
    </header>
  )
}
