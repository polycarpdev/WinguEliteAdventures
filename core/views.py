from django.shortcuts import render
from django.db.models import Q
from destinations.models import Destination
from itineraries.models import Itinerary
from testimonials.models import Testimonial
from blog.models import BlogPost
from .models import TeamMember, FAQ

def home(request):
    featured_destinations = Destination.objects.filter(is_featured=True)[:3]
    featured_itineraries = Itinerary.objects.filter(is_featured=True)[:4]
    featured_testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    recent_posts = BlogPost.objects.filter(is_published=True)[:3]
    
    context = {
        'featured_destinations': featured_destinations,
        'featured_itineraries': featured_itineraries,
        'featured_testimonials': featured_testimonials,
        'recent_posts': recent_posts,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def team(request):
    team_members = TeamMember.objects.all()
    context = {'team_members': team_members}
    return render(request, 'core/team.html', context)

def faqs(request):
    faqs = FAQ.objects.all()
    categories = FAQ.CATEGORY_CHOICES
    
    context = {
        'faqs': faqs,
        'categories': categories,
    }
    return render(request, 'core/faqs.html', context)