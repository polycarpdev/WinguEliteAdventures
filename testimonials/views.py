from django.shortcuts import render
from .models import Testimonial

def testimonial_list(request):
    testimonials = Testimonial.objects.all()
    context = {'testimonials': testimonials}
    return render(request, 'testimonials/list.html', context)