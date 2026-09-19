import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    // Docker Desktop on Windows (WSL2 bind mounts) doesn't reliably forward native
    // filesystem change events into the container, so poll instead to keep hot reload working.
    watch: {
      usePolling: true,
    },
  },
})
