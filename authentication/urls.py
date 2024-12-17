# authentication/urls.py
from django.urls import path
from . import views
from dashboard import views as dashboard_views
from criterion import views as criterion_views
from property import views as property_views  # 导入 property app 的视图
from holdings import views as holdings_views  # 导入 holdings app 的视图

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('index/', views.index, name='index'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('datatable/', property_views.datatable, name='datatable'),  # 更新为 property app 的视图
    path('error/', views.error_503, name='error_503'),
    path('sign-up-wizard/', views.signup_wizard, name='sign-up-wizard'),
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('footer-light', views.footer_light, name='footer-light'),
    path('holdings/', holdings_views.holdings, name='holdings'),    # 更新为 holdings app 的视图 
    path('update_holding_status/', holdings_views.update_holding_status, name='update_holding_status'),
    path('holdings_data/', holdings_views.holdings_data, name='holdings_data'),
    path('criterion/', criterion_views.criterion, name='criterion'),
    path('check-email/', views.check_email, name='check_email'),
    path('report/<int:property_id>/', property_views.report, name='report'),  # 更新为 property app 的视图
    path('agree-to-view/', property_views.agree_to_view, name='agree_to_view'),  # 更新为 property app 的视图
    path('check-agreement/', property_views.check_agreement, name='check_agreement'),
    path('save_user_input/',holdings_views.save_user_input, name='save_user_input'),
    path('profile/',views.profile,name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
]
