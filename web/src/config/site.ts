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
  whatsapp: '254708507364',
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

  stats: [
    { value: '10+', label: 'Years guiding' },
    { value: '100%', label: 'Private tours' },
    { value: 'Kenyan', label: 'Owned & operated' },
    { value: '24h', label: 'Quote turnaround' },
  ],

  developer: {
    name: 'Polycarp Etyang Mubweka',
    handle: '@PolycarpDev',
    url: 'https://linktr.ee/polycarpdev',
    email: 'polycarpdev@gmail.com',
    phone: '+254 708 487 510',
    profiles: {
      github: 'https://github.com/polycarpdev',
      linkedin: 'https://www.linkedin.com/in/polycarpdev/',
      x: '',
      instagram: '',
    } as Record<string, string>,
    showInFooter: true,
  },

  verification: { google: '', bing: '' },
};

export const nav: { label: string; href: string; regions?: boolean }[] = [
  { label: 'Home', href: '/' },
  { label: 'About', href: '/about/' },
  { label: 'Destinations', href: '/destinations/', regions: true },
  { label: 'Packages', href: '/packages/' },
  { label: 'Contact', href: '/contact/' },
  { label: 'FAQ', href: '/faqs/' },
];
