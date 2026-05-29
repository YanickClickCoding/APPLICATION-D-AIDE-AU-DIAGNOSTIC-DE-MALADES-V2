import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
  },
  build: {
    // Seuil d'alerte chunk (par défaut 500kB, on monte à 800kB pour les gros chunks comme ConsultationWorkflow)
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        // Sépare les vendors en chunks distincts — mise en cache navigateur maximale
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'lucide': ['lucide-react'],
          'charts': ['chart.js', 'react-chartjs-2'],
        },
      },
    },
  },
})
