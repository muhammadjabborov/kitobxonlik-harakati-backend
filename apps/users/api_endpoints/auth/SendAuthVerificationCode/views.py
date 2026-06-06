from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.SendAuthVerificationCode.serializers import SendVerificationCodeSerializer
from apps.users.services import CacheTypes, OTPService


class SendAuthVerificationCodeView(GenericAPIView):
    serializer_class = SendVerificationCodeSerializer

    @swagger_auto_schema(request_body=SendVerificationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = str(serializer.validated_data["phone_number"])

        rate_key = f"{CacheTypes.auth_sms_code}_rate:{phone_number}"
        sent_count = cache.get(rate_key, 0)

        if sent_count >= 3:
            raise ValidationError(
                detail={
                    "send_verification_code": _(
                        "You have reached the limit of sending verification code. Try again later."
                    )
                },
                code="limit_exceeded",
            )

        otp_service = OTPService()
        otp_service.send_sms(phone_number)
        cache.set(rate_key, sent_count + 1, timeout=120)

        return Response({"session": otp_service.session})


__all__ = ["SendAuthVerificationCodeView"]
