from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.contrib.auth.models import update_last_login
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.Login.serializers import LoginSerializer
from apps.users.api_endpoints.auth.Register.views import _build_user_data
from apps.users.models import User
from apps.users.services import CacheTypes, generate_cache_key, is_code_valid

from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Login with phone number OTP.

        Send OTP first via `SendAuthVerificationCode`, then submit `phone_number`,
        `code` and `session` received from that endpoint.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = str(serializer.validated_data["phone_number"])
        code = serializer.validated_data["code"]
        session = serializer.validated_data["session"]

        cache_key = generate_cache_key(CacheTypes.auth_sms_code, phone_number, session)
        print(cache_key)
        print(code)
        if not is_code_valid(cache_key, code):
            raise ValidationError(detail={"code": _("Wrong code!")}, code="invalid")

        cache.delete(cache_key)

        user = User.objects.get(phone_number=phone_number)
        update_last_login(None, user)
        token = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(token),
                "access": str(token.access_token),
                "user": _build_user_data(user),
            }
        )


__all__ = ["LoginView"]
