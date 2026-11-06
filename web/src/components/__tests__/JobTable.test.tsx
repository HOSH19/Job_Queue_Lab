import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { Job } from '../../api/client'
import { JobTable } from '../JobTable'

const job: Job = {
  id: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
  type: 'sleep',
  payload: { seconds: 1 },
  status: 'succeeded',
  result: { slept: 1 },
  error: null,
  attempts: 1,
  max_attempts: 3,
  priority: 2,
  run_at: null,
  idempotency_key: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('JobTable', () => {
  it('renders status badge', () => {
    render(<JobTable jobs={[job]} selectedId={null} onSelect={vi.fn()} />)
    expect(screen.getByText('succeeded')).toBeInTheDocument()
    expect(screen.getByText('sleep')).toBeInTheDocument()
  })
})
