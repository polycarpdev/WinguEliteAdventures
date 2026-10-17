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
    plugins: [
      {
        // Dev only: add the trailing slash with a redirect (/cockpit -> /cockpit/,
        // /about -> /about/), as Apache and Django do in production. Registered in a
        // late hook so it runs before Astro's own check, which would 404 instead.
        name: 'trailing-slash-redirect',
        enforce: 'post',
        configureServer(server) {
          return () => {
            server.middlewares.stack.unshift({
              route: '',
              handle(req, res, next) {
                const [path, query = ''] = (req.url ?? '').split('?');
                if (path.endsWith('/') || /\.[a-z0-9]+$/i.test(path) || path.startsWith('/@') || path.startsWith('/_')) return next();
                res.statusCode = 301;
                res.setHeader('Location', `${path}/${query ? `?${query}` : ''}`);
                res.end();
              },
            });
          };
        },
      },
    ],
    server: {
      proxy: {
        // Same paths Apache sends to Django in production.
        '/api': API,
        '/media': API,
        '/cockpit': API,
        '/ckeditor5': API,
        '/static': API,
      },
    },
  },
});
