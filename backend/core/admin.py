from django.contrib import admin
from .models import TeamMember, FAQ

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'order']
    ordering = ['order']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order']
    list_filter = ['category']
    ordering = ['category', 'order']