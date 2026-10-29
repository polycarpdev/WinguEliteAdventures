import { site } from '../config/site';

const abs = (path: string) => new URL(path, site.url).href;
const sameAs = Object.values(site.social).filter(Boolean);

export const ORG_ID = `${site.url}/#organization`;

const devProfiles = Object.values(site.developer.profiles).filter(Boolean);
export const developer = {
  '@type': 'Person',
  name: site.developer.name,
  alternateName: site.developer.handle,
  url: site.developer.url,
  email: site.developer.email,
  telephone: site.developer.phone.replace(/\s/g, ''),
  jobTitle: 'Web Developer',
  address: { '@type': 'PostalAddress', addressLocality: 'Nairobi', addressCountry: 'KE' },
  sameAs: [site.developer.url, ...devProfiles],
};

const DAYS: Record<string, string[]> = {
  'Monday – Friday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
  Saturday: ['Saturday'],
  Sunday: ['Sunday'],
};
const to24h = (t: string) => {
  const m = t.trim().match(/(\d+):(\d+)\s*(AM|PM)/i);
  if (!m) return '';
  let h = Number(m[1]) % 12;
  if (m[3].toUpperCase() === 'PM') h += 12;
  return `${String(h).padStart(2, '0')}:${m[2]}`;
};
const openingHours = () =>
  site.hours
    .filter((h) => h.time !== 'Closed' && DAYS[h.days])
    .map((h) => {
      const [opens, closes] = h.time.split('–').map(to24h);
      return { '@type': 'OpeningHoursSpecification', dayOfWeek: DAYS[h.days], opens, closes };
    });

export function organization() {
  return {
    '@type': ['TravelAgency', 'Organization'],
    '@id': ORG_ID,
    name: site.name,
    alternateName: site.shortName,
    url: `${site.url}/`,
    logo: { '@type': 'ImageObject', url: abs('/brand/logo-640.webp'), width: 640, height: 587 },
    image: abs('/og-default.jpg'),
    description: site.description,
    email: site.email,
    ...(site.phone && { telephone: site.phone.replace(/\s/g, '') }),
    openingHoursSpecification: openingHours(),
    contactPoint: [{
      '@type': 'ContactPoint',
      contactType: 'reservations',
      ...(site.phone && { telephone: site.phone.replace(/\s/g, '') }),
      email: site.bookingsEmail,
      availableLanguage: ['English', 'Swahili'],
      areaServed: 'Worldwide',
    }],
    address: {
      '@type': 'PostalAddress',
      addressLocality: site.address.locality,
      addressCountry: site.address.countryCode,
    },
    areaServed: ['Kenya', 'East Africa', 'Africa'],
    priceRange: '$$$',
    ...(sameAs.length && { sameAs }),
  };
}

export function website() {
  return {
    '@type': 'WebSite',
    '@id': `${site.url}/#website`,
    url: `${site.url}/`,
    name: site.name,
    inLanguage: 'en',
    publisher: { '@id': ORG_ID },
    creator: developer,
  };
}

export function breadcrumbs(items: { name: string; href: string }[]) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: abs(item.href),
    })),
  };
}

export { abs };
