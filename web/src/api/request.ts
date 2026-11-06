/** Thin fetch wrapper with API-key and FastAPI error formatting. */

/** Turn FastAPI `detail` (string | list | object) into a readable message. */
function formatDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg: unknown }).msg)
        }
        return JSON.stringify(item)
      })
      .join('; ')
  }
  if (detail && typeof detail === 'object') return JSON.stringify(detail)
  return 'request failed'
}

/** JSON fetch that always sends Content-Type and optional X-API-Key. */
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const apiKey = localStorage.getItem('jobqueue_api_key')
  const { headers: initHeaders, ...rest } = init ?? {}
  const res = await fetch(path, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(apiKey ? { 'X-API-Key': apiKey } : {}),
      ...(initHeaders ?? {}),
    },
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (body.detail !== undefined) detail = formatDetail(body.detail)
    } catch {
      void 0
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}
