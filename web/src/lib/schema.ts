// schema.org JSON-LD builders. Google uses these for rich results.
import { site } from '../config/site';

const abs = (path: string) => new URL(path, site.url).href;
const sameAs = Object.values(site.social).filter(Boolean);

export const ORG_ID = `${site.url}/#organization`;

export const developer = {
  '@type': 'Person',
  name: site.developer.name,
  url: site.developer.url,
};

export function organization() {
  return {
    '@type': ['TravelAgency', 'Organization'],
    '@id': ORG_ID,
    name: site.name,
    alternateName: site.shortName,
    url: `${site.url}/`,
    logo: abs('/brand/logo-640.webp'),
    image: abs('/og-default.jpg'),
    description: site.description,
    email: site.email,
    ...(site.phone && { telephone: site.phone }),
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
