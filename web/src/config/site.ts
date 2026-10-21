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
  phone: '+254 708 507 364',
  whatsapp: '254708507364', // digits only
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

// Main menu (Gallery, Blog, Our Team and Reviews live in the footer). `regions: true` expands into the Destinations dropdown
// (East Africa, Africa, International…), built from the regions in the cockpit.
export const nav: { label: string; href: string; regions?: boolean }[] = [
  { label: 'Home', href: '/' },
  { label: 'About', href: '/about/' },
  { label: 'Destinations', href: '/destinations/', regions: true },
  { label: 'Packages', href: '/packages/' },
  { label: 'Contact', href: '/contact/' },
  { label: 'FAQ', href: '/faqs/' },
];
