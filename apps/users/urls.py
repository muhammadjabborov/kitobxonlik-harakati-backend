from django.urls import path

from apps.users.api_endpoints import GetProfileView, LoginView, RegisterView, SendAuthVerificationCodeView

app_name = "users"

urlpatterns = [
    # auth
    path(
        "auth/SendAuthVerificationCode/",
        SendAuthVerificationCodeView.as_view(),
        name="send-auth-verification-code",
    ),
    path("auth/Register/", RegisterView.as_view(), name="register"),
    path("auth/Login/", LoginView.as_view(), name="login"),
    # profile
    path("profile/GetProfile/", GetProfileView.as_view(), name="get-profile"),
]
