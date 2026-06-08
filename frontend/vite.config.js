import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

// Inside Docker: BACKEND_HOST=backend:8000
// Local dev:     BACKEND_HOST=localhost:8001 (default)
const BACKEND_HOST = process.env.BACKEND_HOST || 'localhost:8001'
const HTTP_BACKEND  = `http://${BACKEND_HOST}`
const WS_BACKEND    = `ws://${BACKEND_HOST}`

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/graphql': { target: HTTP_BACKEND, changeOrigin: true },
      '/api': {
        target: HTTP_BACKEND,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ws': { target: WS_BACKEND, ws: true, changeOrigin: true },
    },
  },
})
