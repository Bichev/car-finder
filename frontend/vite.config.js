import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command, mode }) => {
  const isDev = command === 'serve'
  
  return {
    plugins: [react()],
    base: '/',
    server: {
      port: 3010,
      host: true,
      watch: {
        usePolling: true, // For Docker environment
      },
      proxy: isDev ? {
        '/api': {
          target: process.env.DOCKER_ENV ? 'http://car-finder-backend:8000' : 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      } : undefined
    },
    build: {
      outDir: 'dist',
      sourcemap: false, // Disable sourcemaps for production
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['lucide-react', 'react-hot-toast']
          }
        }
      }
    },
    define: {
      __API_BASE_URL__: isDev ? '"http://localhost:8000"' : '""'
    }
  }
}) 