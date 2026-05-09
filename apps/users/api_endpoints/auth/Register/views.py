from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.contrib.auth.models import update_last_login
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.Register.serializers import RegisterSerializer
from apps.users.models import User
from apps.users.services import CacheTypes, generate_cache_key, is_code_valid

from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Register a new user.

        Send OTP first via `SendAuthVerificationCode`, then submit all registration
        fields together with `code` and `session` received from that endpoint.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        phone_number = str(data["phone_number"])
        code = data["code"]
        session = data["session"]

        cache_key = generate_cache_key(CacheTypes.auth_sms_code, phone_number, session)
        if not is_code_valid(cache_key, code):
            raise ValidationError(detail={"code": _("Wrong code!")}, code="invalid")

        cache.delete(cache_key)

        user = User.objects.create_user(
            phone_number=phone_number,
            full_name=data["full_name"],
            age=data.get("age"),
            grade=data.get("grade"),
            region=data.get("region"),
            school_number=data.get("school_number"),
            identity_type=data.get("identity_type"),
            identity_number=data.get("identity_number"),
        )

        update_last_login(None, user)
        token = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(token),
                "access": str(token.access_token),
                "user": _build_user_data(user),
            },
            status=201,
        )


def _build_user_data(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "age": user.age,
        "grade": user.grade,
        "school_number": user.school_number,
        "region": user.region_id,
        "identity_type": user.identity_type,
        "identity_number": user.identity_number,
    }


__all__ = ["RegisterView"]
