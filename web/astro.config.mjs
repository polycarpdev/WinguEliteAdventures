import { readFileSync } from 'node:fs';
import { defineConfig, passthroughImageService } from 'astro/config';

let packageSlugs = [];
try {
  packageSlugs = JSON.parse(readFileSync(new URL('./src/data/content.json', import.meta.url), 'utf8')).itineraries.map((i) => i.slug);
} catch {}

const API = process.env.API_ORIGIN ?? 'http://127.0.0.1:8000';

export default defineConfig({
  site: 'https://wingueliteadventures.co.ke',
  trailingSlash: 'always',
  compressHTML: true,
  redirects: {
    '/destinations/kenya/': '/destinations/east-africa/kenya/',
    '/itineraries/': '/packages/',
    ...Object.fromEntries(packageSlugs.map((slug) => [`/itineraries/${slug}/`, `/packages/${slug}/`])),
  },
  scopedStyleStrategy: 'class',
  build: {
    format: 'directory',
    concurrency: 1,
    inlineStylesheets: 'always',
  },
  prefetch: { prefetchAll: true, defaultStrategy: 'viewport' },
  image: { service: passthroughImageService() },
  devToolbar: { enabled: false },
  vite: {
    plugins: [
      {
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
        '/api': API,
        '/media': API,
        '/cockpit': API,
        '/ckeditor5': API,
        '/static': API,
      },
    },
  },
});
