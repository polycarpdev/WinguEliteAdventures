// Business details in one place. Empty values are hidden on the site,
// so placeholders never reach visitors.
export const site = {
  name: 'Wingu Elite Adventures',
  shortName: 'Wingu Elite',
  url: 'https://wingueliteadventures.co.ke',
  tagline: 'Luxury Kenya Safari Adventures',
  description:
    'Wingu Elite Adventures is a Kenyan-owned luxury safari company crafting private, bespoke journeys to the Masai Mara, Amboseli, Mount Kenya, Diani and beyond.',
  locale: 'en_KE',
  currency: 'USD',

  email: 'info@wingueliteadventures.co.ke',
  bookingsEmail: 'bookings@wingueliteadventures.co.ke',
  phone: '', // e.g. '+254 712 345 678'
  whatsapp: '', // digits only, e.g. '254712345678'
  address: { locality: 'Nairobi', country: 'Kenya', countryCode: 'KE' },
  hours: [
    { days: 'Monday – Friday', time: '8:00 AM – 6:00 PM' },
    { days: 'Saturday', time: '9:00 AM – 4:00 PM' },
    { days: 'Sunday', time: 'Closed' },
  ],
  social: {
    instagram: '',
    facebook: '',
    tiktok: '',
    youtube: '',
    tripadvisor: '',
  } as Record<string, string>,

  // Shown in the hero trust strip; confirm before launch.
  stats: [
    { value: '10+', label: 'Years guiding' },
    { value: '100%', label: 'Private tours' },
    { value: 'Kenyan', label: 'Owned & operated' },
    { value: '24h', label: 'Quote turnaround' },
  ],

  // Developer credit (footer, humans.txt, meta, JSON-LD).
  developer: { name: 'polycarp dev', url: 'https://linktr.ee/polycarpdev' },
};

export const nav = [
  { label: 'Destinations', href: '/destinations/kenya/' },
  { label: 'Safaris', href: '/itineraries/' },
  { label: 'Gallery', href: '/gallery/' },
  { label: 'Journal', href: '/blog/' },
  { label: 'About', href: '/about/' },
  { label: 'Contact', href: '/contact/' },
];
