from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory

def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    categories = BlogCategory.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'blog/list.html', context)

def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = category.posts.filter(is_published=True)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/detail.html', context)