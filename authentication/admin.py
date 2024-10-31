from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'birth_date')

admin.site.register(UserProfile, UserProfileAdmin)