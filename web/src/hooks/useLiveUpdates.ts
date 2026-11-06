/**
 * Prefer WebSocket refresh; fall back to 1s polling when the socket is down.
 * Connect is delayed so React Strict Mode remounts do not flap the socket.
 */

import { useEffect, useState } from 'react'
import { jobsWebSocketUrl } from '../api/client'

export function useLiveUpdates(refresh: () => void | Promise<void>): boolean {
  const [live, setLive] = useState(false)

  useEffect(() => {
    let socket: WebSocket | null = null
    let pollId: number | undefined
    let closed = false

    function startPolling() {
      if (pollId !== undefined) return
      pollId = window.setInterval(() => {
        void refresh()
      }, 1000)
    }

    const connectId = window.setTimeout(() => {
      if (closed) return
      try {
        socket = openSocket({
          onLive: () => {
            setLive(true)
            void refresh()
          },
          onMessage: () => void refresh(),
          onDown: () => {
            setLive(false)
            startPolling()
          },
          shouldClose: () => closed,
        })
      } catch {
        startPolling()
      }
    }, 100)

    return () => {
      closed = true
      window.clearTimeout(connectId)
      socket?.close()
      if (pollId !== undefined) window.clearInterval(pollId)
    }
  }, [refresh])

  return live
}

function openSocket(handlers: {
  onLive: () => void
  onMessage: () => void
  onDown: () => void
  shouldClose: () => boolean
}): WebSocket {
  /** Wire a WebSocket to the provided lifecycle callbacks. */
  const socket = new WebSocket(jobsWebSocketUrl())
  socket.onopen = () => {
    if (handlers.shouldClose()) {
      socket.close()
      return
    }
    handlers.onLive()
  }
  socket.onmessage = () => handlers.onMessage()
  socket.onerror = () => handlers.onDown()
  socket.onclose = () => {
    if (!handlers.shouldClose()) handlers.onDown()
  }
  return socket
}
