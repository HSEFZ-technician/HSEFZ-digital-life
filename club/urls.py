from django.urls import path, re_path
from .views import register_view, login_view, activate_email_view, manual_activate_view, modify_password_view, send_modify_password_email_view, home_view, logout_view, user_security_view, selection_sign_up_view, selection_desc_view, user_info_view,event_manage_view,modify_event_view,notice_view,notice_manage_view,modify_notice_view

app_name = 'club'
urlpatterns = [
    path('register/', register_view, name = 'register'),
    re_path(r'^login/$', login_view, name = 'login'),
    path('activate_email/<token>/', activate_email_view, name = 'activate_email'),
    path('manual_activate/', manual_activate_view, name = 'manual_activate'),
    path('modify_password/<token>/', modify_password_view, name = 'modify_password'),
    path('send_modify_password_email/',send_modify_password_email_view, name = 'send_modify_password_email'),
    path('', home_view, name = 'home'),
    path('logout/', logout_view, name = 'logout'),
    path('user_security/', user_security_view, name='user_security'),
    path('selection_sign_up/', selection_sign_up_view, name='selection_sign_up'),
    path('selection_desc/',selection_desc_view, name='selection_desc'),
    path('user_info/',user_info_view, name='user_info'),
    path('event_manage/',event_manage_view,name='event_manage'),
    path('modify_event/',modify_event_view,name='modify_event'),
    path('notice/<int:id>/',notice_view,name='notice'),
    path('notice_manage/',notice_manage_view,name="notice_manage"),
    path('modify_notice/',modify_notice_view,name="modify_notice")
]