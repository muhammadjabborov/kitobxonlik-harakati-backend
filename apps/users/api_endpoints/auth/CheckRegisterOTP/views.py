from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.contrib.auth.models import update_last_login
from django.core.cache import cache
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.CheckRegisterOTP.serializers import (
    CheckRegisterOTPSerializer,
)
from apps.users.api_endpoints.auth.utils import build_token_response
from apps.users.models import User
from apps.users.services import CacheTypes, generate_cache_key, is_code_valid


class CheckRegisterOTPView(generics.GenericAPIView):
    serializer_class = CheckRegisterOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = serializer.validated_data["session"]
        code = serializer.validated_data["code"]

        form_key = generate_cache_key(CacheTypes.register_form_data, session)
        data = cache.get(form_key)
        if not data:
            raise ValidationError(
                detail={
                    "session": _(
                        "Session expired or not found. Please re-submit the register form."
                    )
                },
                code="invalid",
            )

        phone_number = data["phone_number"]
        otp_key = generate_cache_key(CacheTypes.register_sms_code, phone_number, session)
        if not is_code_valid(otp_key, code):
            raise ValidationError(detail={"code": _("Wrong code!")}, code="invalid")

        if User.objects.filter(phone_number=phone_number).exists():
            cache.delete(form_key)
            cache.delete(otp_key)
            raise ValidationError(
                detail={
                    "phone_number": _("A user with this phone number already exists.")
                },
                code="already_exists",
            )

        identity_number = data.get("identity_number")
        if identity_number and User.objects.filter(identity_number=identity_number).exists():
            cache.delete(form_key)
            cache.delete(otp_key)
            raise ValidationError(
                detail={
                    "identity_number": _(
                        "A user with this identity number already exists."
                    )
                },
                code="already_exists",
            )

        with transaction.atomic():
            user = User.objects.create_user(
                phone_number=phone_number,
                full_name=data["full_name"],
                birth_date=data.get("birth_date"),
                grade=data.get("grade"),
                region_id=data.get("region"),
                identity_type=data.get("identity_type"),
                identity_number=identity_number,
            )

        cache.delete(form_key)
        cache.delete(otp_key)

        update_last_login(None, user)
        return Response(build_token_response(user), status=status.HTTP_201_CREATED)


__all__ = ["CheckRegisterOTPView"]
