from django.db import models

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/')
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.role}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('packing', 'Packing'),
        ('safari_tips', 'Safari Tips'),
        ('general', 'General'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question