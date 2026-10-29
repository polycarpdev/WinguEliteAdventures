import type { APIRoute } from 'astro';
import type { Img } from '../lib/content';
import { destinations, itineraries, posts, categories, gallery, content, regions, liveCountries, countryUrl, coverFor, inRegion, inCountry } from '../lib/content';

const SITE = 'https://wingueliteadventures.co.ke';

type Pic = { img: Img | null; caption?: string };
type Entry = { loc: string; lastmod?: string; priority: number; images?: Pic[] };

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const abs = (src: string) => (src.startsWith('http') ? src : SITE + src);

export const GET: APIRoute = () => {
  const built = content.generated_at;
  const entries: Entry[] = [
    { loc: '/', lastmod: built, priority: 1.0 },
    { loc: '/packages/', lastmod: built, priority: 0.9 },
    { loc: '/destinations/', lastmod: built, priority: 0.9 },
    ...regions.map((r) => ({
      loc: `/destinations/${r.slug}/`, lastmod: built, priority: 0.85,
      images: [{ img: coverFor(r.image, inRegion(r.slug)), caption: r.name }],
    })),
    ...regions.flatMap((r) => liveCountries(r).map((c) => ({
      loc: countryUrl(r.slug, c.slug), lastmod: built, priority: 0.85,
      images: [{ img: coverFor(c.image, inCountry(c.slug)), caption: `${c.name} safaris` }],
    }))),
    { loc: '/bookings/', priority: 0.8 },
    { loc: '/about/', priority: 0.7 },
    { loc: '/team/', priority: 0.5 },
    { loc: '/faqs/', priority: 0.6 },
    { loc: '/blog/', lastmod: posts[0]?.updated_at, priority: 0.7 },
    { loc: '/gallery/', priority: 0.6 },
    { loc: '/testimonials/', priority: 0.6 },
    { loc: '/contact/', priority: 0.6 },
    ...itineraries.map((i) => ({
      loc: `/packages/${i.slug}/`, lastmod: i.updated_at, priority: 0.9,
      images: [{ img: i.image, caption: `${i.title} (${i.duration_label})` }],
    })),
    ...destinations.map((d) => ({
      loc: `/destinations/detail/${d.slug}/`, lastmod: d.updated_at, priority: 0.8,
      images: [{ img: d.image, caption: `${d.name}, ${d.country.name}` }],
    })),
    ...posts.map((p) => ({ loc: `/blog/${p.slug}/`, lastmod: p.updated_at, priority: 0.7, images: [{ img: p.image, caption: p.title }] })),
    ...categories.map((c) => ({ loc: `/blog/category/${c.slug}/`, priority: 0.4 })),
    ...gallery.map((a) => ({
      loc: `/gallery/album/${a.slug}/`, lastmod: a.created_at, priority: 0.5,
      images: [{ img: a.cover, caption: a.name }, ...a.images.map((x) => ({ img: x.image, caption: x.caption || a.name }))],
    })),
  ];

  const imageXml = (pics: Pic[] = []) =>
    pics
      .filter((p) => p.img)
      .slice(0, 1000)
      .map((p) => `<image:image><image:loc>${esc(abs(p.img!.src))}</image:loc>${p.caption ? `<image:caption>${esc(p.caption)}</image:caption>` : ''}</image:image>`)
      .join('');

  const xml =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' +
    entries
      .map((e) =>
        `  <url><loc>${SITE}${e.loc}</loc>${e.lastmod ? `<lastmod>${e.lastmod.slice(0, 10)}</lastmod>` : ''}` +
        `<priority>${e.priority.toFixed(1)}</priority>${imageXml(e.images)}</url>`)
      .join('\n') +
    '\n</urlset>\n';
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
