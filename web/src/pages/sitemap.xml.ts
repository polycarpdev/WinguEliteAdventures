import type { APIRoute } from 'astro';
import { destinations, itineraries, posts, categories, gallery, content, regions, liveCountries, countryUrl } from '../lib/content';

const SITE = 'https://wingueliteadventures.co.ke';

export const GET: APIRoute = () => {
  const built = content.generated_at;
  const entries: { loc: string; lastmod?: string; priority: number }[] = [
    { loc: '/', lastmod: built, priority: 1.0 },
    { loc: '/packages/', lastmod: built, priority: 0.9 },
    { loc: '/destinations/', lastmod: built, priority: 0.9 },
    ...regions.map((r) => ({ loc: `/destinations/${r.slug}/`, lastmod: built, priority: 0.85 })),
    ...regions.flatMap((r) => liveCountries(r).map((c) => ({ loc: countryUrl(r.slug, c.slug), lastmod: built, priority: 0.85 }))),
    { loc: '/bookings/', priority: 0.8 },
    { loc: '/about/', priority: 0.7 },
    { loc: '/team/', priority: 0.5 },
    { loc: '/faqs/', priority: 0.6 },
    { loc: '/blog/', lastmod: posts[0]?.updated_at, priority: 0.7 },
    { loc: '/gallery/', priority: 0.6 },
    { loc: '/testimonials/', priority: 0.6 },
    { loc: '/contact/', priority: 0.6 },
    ...itineraries.map((i) => ({ loc: `/packages/${i.slug}/`, lastmod: i.updated_at, priority: 0.9 })),
    ...destinations.map((d) => ({ loc: `/destinations/detail/${d.slug}/`, lastmod: d.updated_at, priority: 0.8 })),
    ...posts.map((p) => ({ loc: `/blog/${p.slug}/`, lastmod: p.updated_at, priority: 0.7 })),
    ...categories.map((c) => ({ loc: `/blog/category/${c.slug}/`, priority: 0.4 })),
    ...gallery.map((a) => ({ loc: `/gallery/album/${a.slug}/`, lastmod: a.created_at, priority: 0.5 })),
  ];
  const xml =
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    entries
      .map((e) => `  <url><loc>${SITE}${e.loc}</loc>${e.lastmod ? `<lastmod>${e.lastmod.slice(0, 10)}</lastmod>` : ''}<priority>${e.priority.toFixed(1)}</priority></url>`)
      .join('\n') +
    '\n</urlset>\n';
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
