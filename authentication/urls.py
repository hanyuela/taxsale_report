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
    path('forget-password/', views.forget_password, name='forget_password'),
    path('error/', views.error_503, name='error_503'),
    path('sign-up-wizard/', views.signup_wizard, name='sign-up-wizard'),
    path('confirm-password-reset/<int:user_id>/<uuid:token>/', views.confirm_password_reset, name='confirm_password_reset'),
]
