from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'investment_amount')  # 移除了不存在的字段

admin.site.register(UserProfile, UserProfileAdmin)
