from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),  # 将根路径设置为登录页面
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('index/', views.index, name='index'),  # 访问主页后跳转到 index 页面
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('datatable/', views.datatable, name='datatable'),
    path('error/', views.error_503, name='error_503'),
    path('sign-up-wizard/', views.signup_wizard, name='sign-up-wizard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('footer-light', views.footer_light, name='footer-light'),
    path('holdings/', views.holdings, name='holdings'),
    path('criterion/', views.criterion, name='criterion'),
]
