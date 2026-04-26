import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'url';

export default defineConfig({
  plugins: [svelte({ hot: false })],
  resolve: {
    alias: [
      {
        find: /^svelte$/,
        replacement: fileURLToPath(
          new URL('./node_modules/svelte/src/index-client.js', import.meta.url)
        ),
      },
    ],
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
});
