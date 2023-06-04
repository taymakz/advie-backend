from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path('user/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/logout/', views.LogoutView.as_view(), name='logout'),

    # path('user/current/password/', views.ChangePasswordView.as_view(), name='current_user_change_password'),

    path('user/request/current/', views.RequestCurrentUserView.as_view(), name='request_current_user'),
    path('user/request/otp/', views.RequestOTPView.as_view(), name='request_otp'),

    # Authenticate
    path('user/authenticate/check/', views.AuthenticationCheckView.as_view(), name='authenticate_check'),
    path('user/authenticate/password/', views.PasswordAuthenticationView.as_view(), name='authenticate_password'),
    path('user/authenticate/otp/', views.OTPAuthenticationView.as_view(), name='authenticate_otp'),

    path('user/forgot/password/check/', views.ForgotPasswordCheckView.as_view(), name='forgot_password_check'),
    path('user/forgot/password/otp/', views.ForgotPasswordOTPView.as_view(), name='forgot_password_otp'),
    path('user/forgot/password/reset/', views.ForgotPasswordResetView.as_view(), name='forgot_password_otp'),
    # path('auth/login/', views.LoginView.as_view(), name='login'),
    # path('auth/reset/', views.ResetPasswordView.as_view(), name='reset_password'),

]
