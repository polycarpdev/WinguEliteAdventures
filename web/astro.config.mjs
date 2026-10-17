// @ts-check
import { defineConfig, passthroughImageService } from 'astro/config';

// Django dev server the Astro dev server proxies forms and media to.
const API = process.env.API_ORIGIN ?? 'http://127.0.0.1:8000';

export default defineConfig({
  site: 'https://wingueliteadventures.co.ke',
  trailingSlash: 'always', // matches the old Django URLs exactly
  compressHTML: true,
  // Scope class travels with the `class` prop, so parents can style child components.
  scopedStyleStrategy: 'class',
  build: {
    format: 'directory',
    concurrency: 1, // shared hosting: one page at a time
    inlineStylesheets: 'always', // no render-blocking CSS request
  },
  // Pages are prefetched as links scroll into view; with <ClientRouter />
  // navigation then swaps the DOM instantly, app-style.
  prefetch: { prefetchAll: true, defaultStrategy: 'viewport' },
  // Images are pre-optimised by Django/Pillow (WebP + srcset); no sharp.
  image: { service: passthroughImageService() },
  devToolbar: { enabled: false },
  vite: {
    server: {
      proxy: {
        '/api': API,
        '/media': API,
      },
    },
  },
});
