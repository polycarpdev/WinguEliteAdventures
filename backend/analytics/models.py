from django.db import models

class PageView(models.Model):

    DEVICE_CHOICES = [('mobile', 'Mobile'), ('tablet', 'Tablet'), ('desktop', 'Desktop')]

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.CharField(max_length=300, db_index=True)
    referrer = models.CharField(max_length=200, blank=True, help_text='Referring host, empty for direct/internal')
    visitor = models.CharField(max_length=16, db_index=True)
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES)
    browser = models.CharField(max_length=30, blank=True)
    timezone = models.CharField(max_length=60, blank=True)
    language = models.CharField(max_length=10, blank=True)
    is_entry = models.BooleanField(default=False, help_text='First page of a visit (arrived from outside the site)')

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at', 'visitor'])]

    def __str__(self):
        return f'{self.path} @ {self.created_at:%Y-%m-%d %H:%M}'
