import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// LOCAL DEVELOPMENT ONLY: inject the backend API key from the Vite server process.
// Never expose CLINICAL_API_KEY via VITE_* or browser JavaScript.
const apiKey = process.env.CLINICAL_API_KEY;
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        configure(proxy) {
          proxy.on('proxyReq', proxyReq => {
            if (apiKey) proxyReq.setHeader('x-api-key', apiKey);
          });
        }
      },
      '/health': 'http://127.0.0.1:8000'
    }
  }
});
