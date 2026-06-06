from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.CheckPhoneNumber.serializers import CheckPhoneNumberSerializer
from apps.users.models import User
from apps.users.services import CacheTypes, OTPService


class CheckPhoneNumberView(GenericAPIView):
    serializer_class = CheckPhoneNumberSerializer

    @swagger_auto_schema(request_body=CheckPhoneNumberSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = str(serializer.validated_data["phone_number"])

        registered = User.objects.filter(phone_number=phone_number).exists()

        if not registered:
            return Response({"registered": False})

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

        return Response({"registered": True, "session": otp_service.session})


__all__ = ["CheckPhoneNumberView"]
