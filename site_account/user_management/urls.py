from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),



    path('request/current/', views.RequestCurrentUserView.as_view(), name='request_current_user'),
    path('request/otp/', views.RequestOTPView.as_view(), name='request_otp'),



    # Authenticate
    path('authenticate/check/', views.AuthenticationCheckView.as_view(), name='authenticate_check'),
    path('authenticate/password/', views.PasswordAuthenticationView.as_view(), name='authenticate_password'),
    path('authenticate/otp/', views.OTPAuthenticationView.as_view(), name='authenticate_otp'),

    # Forgot password
    path('forgot/password/check/', views.ForgotPasswordCheckView.as_view(), name='forgot_password_check'),
    path('forgot/password/otp/', views.ForgotPasswordOTPView.as_view(), name='forgot_password_otp'),
    path('forgot/password/reset/', views.ForgotPasswordResetView.as_view(), name='forgot_password_otp'),

    # User Detail
    path('edit/detail/', views.UserUpdateDetailView.as_view(), name='user_edit_detail'),
    path('edit/password/', views.UserEditPassword.as_view(), name='user_edit_password'),

    path('edit/phone/request/', views.UserEditPhoneRequestView.as_view(), name='user_edit_phone_request'),
    path('edit/phone/confirm/', views.UserEditPhoneConfirmView.as_view(), name='user_edit_phone_confirm'),

    path('edit/email/request/', views.UserEditEmailRequestView.as_view(), name='user_edit_email_request'),
    path('edit/email/confirm/', views.UserEditEmailConfirmView.as_view(), name='user_edit_email_confirm'),
]
