import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:8007',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://websocket_server:8008',
        ws: true,
      },
    },
  },
  define: {
    'process.env': process.env,
  },
});
