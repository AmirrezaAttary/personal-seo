from django.contrib.sitemaps import Sitemap
from .models import Business


class BusinessSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Business.objects.all()
    
    def lastmod(self, obj):
        return obj.created_at