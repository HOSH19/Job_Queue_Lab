import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

/** Vite config: React plugin and HTTP proxy to the FastAPI process. */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/jobs': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/metrics': 'http://127.0.0.1:8000',
      '/dlq': 'http://127.0.0.1:8000',
    },
  },
})
