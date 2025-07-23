from django.urls import path

from . import api_views, template_views

urlpatterns = [
    # API эндпоинты
    path('api/request-code/', api_views.RequestCodeView.as_view(), name='api_request_code'),
    path('api/verify-code/', api_views.VerifyCodeView.as_view(), name='api_verify_code'),
    path('api/profile/', api_views.ProfileView.as_view(), name='api_profile'),
    path('api/activate-invite-code/', api_views.ActivateInviteCodeView.as_view(), name='api_activate_invite_code'),

    # Веб интерфейс
    path('login-phone/', template_views.LoginPhoneView.as_view(), name='login_phone'),
    path('verify-code/', template_views.VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', template_views.ProfileView.as_view(), name='profile'),
    path('activate-code/', template_views.ActivateInviteCodeView.as_view(), name='activate_code'),

]
