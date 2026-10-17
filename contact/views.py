from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage

def contact(request):
    if request.method == 'POST':
        contact_msg = ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        
        # Send email notification
        subject = f'New Contact Message: {contact_msg.subject}'
        message = f'''
        New contact message received:
        
        Name: {contact_msg.name}
        Email: {contact_msg.email}
        Phone: {contact_msg.phone}
        Subject: {contact_msg.subject}
        
        Message:
        {contact_msg.message}
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except:
            pass
        
        messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        return redirect('contact:success')
    
    return render(request, 'contact/contact.html')

def contact_success(request):
    return render(request, 'contact/success.html')