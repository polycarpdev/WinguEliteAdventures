import type { APIRoute } from 'astro';
import { site } from '../config/site';

// humanstxt.org: credits the people behind the site (independent of the footer).
export const GET: APIRoute = () =>
  new Response(
    [
      '/* TEAM */',
      `  Developer & designer: ${site.developer.name} (${site.developer.handle})`,
      `  Portfolio: ${site.developer.url}`,
      `  Email: ${site.developer.email}`,
      `  Phone: ${site.developer.phone}`,
      ...Object.entries(site.developer.profiles).filter(([, v]) => v).map(([k, v]) => `  ${k[0].toUpperCase() + k.slice(1)}: ${v}`),
      '  Location: Nairobi, Kenya',
      '',
      '/* SITE */',
      `  Client: ${site.name}`,
      `  Last update: ${new Date().toISOString().slice(0, 10)}`,
      '  Language: English',
      '  Standards: HTML5, CSS3, schema.org, Open Graph',
      '  Components: Astro, Django, Pillow',
      '',
    ].join('\n'),
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  );
