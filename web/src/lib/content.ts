// Typed access to the content exported by Django (`manage.py export_content`).
import raw from '../data/content.json';

export interface Img {
  src: string;
  srcset: string;
  width: number;
  height: number;
  original: string;
  alt: string;
}

export interface Destination {
  id: number;
  name: string;
  slug: string;
  country: 'kenya' | 'international';
  short_description: string;
  description_html: string;
  image: Img | null;
  is_featured: boolean;
  updated_at: string;
}

export interface ItineraryDay {
  day_number: number;
  title: string;
  description_html: string;
}

export interface Itinerary {
  id: number;
  title: string;
  slug: string;
  destination: { name: string; slug: string; country: string };
  duration_days: number;
  difficulty: string;
  difficulty_label: string;
  max_group_size: number;
  price_from: number;
  overview_html: string;
  includes_html: string;
  excludes_html: string;
  image: Img | null;
  is_featured: boolean;
  updated_at: string;
  days: ItineraryDay[];
}

export interface Post {
  id: number;
  title: string;
  slug: string;
  author: string;
  category: { name: string; slug: string } | null;
  image: Img | null;
  excerpt: string;
  content_html: string;
  published_date: string;
  updated_at: string;
}

export interface Album {
  name: string;
  slug: string;
  description: string;
  cover: Img | null;
  created_at: string;
  images: { image: Img | null; caption: string }[];
}

export interface Testimonial {
  id: number;
  client_name: string;
  photo: Img | null;
  trip: { title: string; slug: string } | null;
  rating: number;
  review: string;
  date: string;
  is_featured: boolean;
}

export interface Content {
  generated_at: string;
  site_url: string;
  destinations: Destination[];
  itineraries: Itinerary[];
  blog: { categories: { name: string; slug: string }[]; posts: Post[] };
  gallery: Album[];
  testimonials: Testimonial[];
  team: { name: string; role: string; bio: string; photo: Img | null }[];
  faq_categories: { value: string; label: string }[];
  faqs: { category: string; question: string; answer: string }[];
}

export const content = raw as unknown as Content;
export const { destinations, itineraries, gallery, testimonials, team, faqs } = content;
export const posts = content.blog.posts;
export const categories = content.blog.categories.filter((c) => posts.some((p) => p.category?.slug === c.slug));

export const COUNTRIES = {
  kenya: { label: 'Kenya', title: 'Kenya Safari Destinations' },
  international: { label: 'Beyond Kenya', title: 'International Destinations' },
} as const;

export const byCountry = (country: string) => destinations.filter((d) => d.country === country);
export const itinerariesFor = (destSlug: string) => itineraries.filter((i) => i.destination.slug === destSlug);

/** Hero photo: the company's own gallery shots first, then featured destinations. */
export const heroImage: Img | null =
  gallery.flatMap((a) => [a.cover, ...a.images.map((i) => i.image)]).find((i) => i && i.width >= 1600) ??
  destinations.find((d) => d.image && d.image.width >= 1300)?.image ??
  null;

export const usd = (n: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);

export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });

export const stripHtml = (html: string) =>
  html
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&#39;|&rsquo;/g, '’')
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ')
    .trim();

/** Trim to a meta-description-friendly length on a word boundary. */
export const clip = (text: string, max = 158) => {
  const t = stripHtml(text);
  if (t.length <= max) return t;
  return t.slice(0, t.lastIndexOf(' ', max - 1)).replace(/[,.;:\s]+$/, '') + '…';
};

export const readingMinutes = (html: string) => Math.max(1, Math.round(stripHtml(html).split(' ').length / 220));

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** Plain-text field (e.g. FAQ answer) to safe HTML paragraphs. */
export const paragraphs = (text: string) =>
  escapeHtml(text)
    .split(/\n{2,}/)
    .map((p) => `<p>${p.replace(/\n/g, '<br />')}</p>`)
    .join('');
