from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('adminsoyhome/', admin.site.urls),
    path('', include('authentication.urls')),  # 引入 authentication 应用的 URL 配置
    
]
