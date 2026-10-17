from django.contrib.sitemaps import Sitemap

class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return [
            '/',
            '/about/',
            '/team/',
            '/faqs/',
            '/itineraries/',
            '/destinations/kenya/',
            '/destinations/international/',
            '/blog/',
            '/gallery/',
            '/testimonials/',
            '/contact/',
        ]

    def location(self, item):
        return item