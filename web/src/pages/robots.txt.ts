import type { APIRoute } from 'astro';
export const GET: APIRoute = () =>
  new Response(
    ['User-agent: *', 'Allow: /', 'Disallow: /admin/', 'Disallow: /cockpit/', 'Disallow: /api/', 'Disallow: /bookings/success/', 'Disallow: /contact/success/', '', 'Sitemap: https://wingueliteadventures.co.ke/sitemap.xml', ''].join('\n'),
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  );
