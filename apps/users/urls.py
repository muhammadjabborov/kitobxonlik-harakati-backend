from django.urls import path

from apps.users.api_endpoints import (
    CheckPhoneNumberView,
    CheckRegisterOTPView,
    GetProfileView,
    LoginView,
    RegisterView,
    SendAuthVerificationCodeView,
)

app_name = "users"

urlpatterns = [
    path(
        "auth/CheckPhoneNumber/",
        CheckPhoneNumberView.as_view(),
        name="check-phone-number",
    ),
    path(
        "auth/SendAuthVerificationCode/",
        SendAuthVerificationCodeView.as_view(),
        name="send-auth-verification-code",
    ),
    path("auth/Login/", LoginView.as_view(), name="login"),
    path("auth/Register/", RegisterView.as_view(), name="register"),
    path(
        "auth/CheckRegisterOTP/",
        CheckRegisterOTPView.as_view(),
        name="check-register-otp",
    ),
    path("profile/GetProfile/", GetProfileView.as_view(), name="get-profile"),
]
