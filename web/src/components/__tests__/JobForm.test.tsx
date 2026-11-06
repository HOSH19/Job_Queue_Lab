import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { JobForm } from '../JobForm'

vi.mock('../../api/client', () => ({
  createJob: vi.fn(async () => ({
    id: 'abc',
    type: 'sleep',
    payload: { seconds: 2 },
    status: 'queued',
    result: null,
    error: null,
    attempts: 0,
    max_attempts: 3,
    priority: 0,
    run_at: null,
    idempotency_key: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  })),
}))

import { createJob } from '../../api/client'

describe('JobForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('submits a sleep job', async () => {
    const user = userEvent.setup()
    const onCreated = vi.fn()
    render(<JobForm onCreated={onCreated} />)

    await user.click(screen.getByRole('button', { name: /submit/i }))

    expect(createJob).toHaveBeenCalled()
    expect(onCreated).toHaveBeenCalledWith(expect.objectContaining({ id: 'abc' }))
  })

  it('switches payload fields by type', async () => {
    const user = userEvent.setup()
    render(<JobForm onCreated={vi.fn()} />)

    await user.selectOptions(screen.getByLabelText(/type/i), 'fail')
    expect(screen.getByLabelText(/error message/i)).toBeInTheDocument()
  })
})
