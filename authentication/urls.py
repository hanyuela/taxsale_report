from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.index, name='index'),
    path('template/index.html', views.template_index, name='template_index'),  # 新增路径
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('datatable/', views.datatable, name='datatable'),
    path('error/', views.error_503, name='error_503'),
    path('sign-up-wizard/', views.signup_wizard, name='sign-up-wizard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password, name='reset_password'),
]
