from django.shortcuts import render, get_object_or_404
from .models import GalleryAlbum, GalleryImage

def gallery_index(request):
    albums = GalleryAlbum.objects.all()
    context = {'albums': albums}
    return render(request, 'gallery/index.html', context)

def album_detail(request, slug):
    album = get_object_or_404(GalleryAlbum, slug=slug)
    images = album.images.all()
    
    context = {
        'album': album,
        'images': images,
    }
    return render(request, 'gallery/album_detail.html', context)