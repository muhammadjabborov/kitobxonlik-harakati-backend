from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.Register.serializers import RegisterSerializer
from apps.users.services import CacheTypes, OTPService, generate_cache_key

REGISTER_FORM_TTL = 600
REGISTER_RATE_LIMIT = 3
REGISTER_RATE_WINDOW = 120


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        phone_number = str(data["phone_number"])
        data["phone_number"] = phone_number
        region = data.get("region")
        if region is not None:
            data["region"] = region.pk

        rate_key = f"{CacheTypes.register_sms_code}_rate:{phone_number}"
        sent_count = cache.get(rate_key, 0)
        if sent_count >= REGISTER_RATE_LIMIT:
            raise ValidationError(
                detail={
                    "send_verification_code": _(
                        "You have reached the limit of sending verification code. Try again later."
                    )
                },
                code="limit_exceeded",
            )

        otp_service = OTPService(
            cache_type=CacheTypes.register_sms_code,
            timeout=REGISTER_FORM_TTL,
        )
        otp_service.send_sms(phone_number)
        cache.set(rate_key, sent_count + 1, timeout=REGISTER_RATE_WINDOW)

        form_key = generate_cache_key(CacheTypes.register_form_data, otp_service.session)
        cache.set(form_key, data, timeout=REGISTER_FORM_TTL)

        return Response({"session": otp_service.session})


__all__ = ["RegisterView"]
