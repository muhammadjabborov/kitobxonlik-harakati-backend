from adrf.views import APIView
from asgiref.sync import sync_to_async
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.core.cache import cache
from django.db.transaction import non_atomic_requests
from django.utils.translation import gettext_lazy as _

from apps.users.api_endpoints.auth.SendAuthVerificationCode.serializers import (
    SendVerificationCodeSerializer,
)
from apps.users.services import CacheTypes, MessageProvider


class SendAuthVerificationCodeView(APIView):
    serializer_class = SendVerificationCodeSerializer

    @non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(request_body=SendVerificationCodeSerializer)
    async def post(self, request, *args, **kwargs):
        """`phone_number` format E164 as like `+998945552233`"""
        serializer = self.serializer_class(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        phone_number = str(serializer.validated_data["phone_number"])

        rate_key = f"{CacheTypes.auth_sms_code}_rate:{phone_number}"
        sent_count = await sync_to_async(cache.get)(rate_key, 0)

        if sent_count >= 3:
            raise ValidationError(
                detail={
                    "send_verification_code": _(
                        "You have reached the limit of sending verification code. Try again later."
                    )
                },
                code="limit_exceeded",
            )

        message_provider = MessageProvider()
        await message_provider.send_sms(phone_number)

        await sync_to_async(cache.set)(rate_key, sent_count + 1, timeout=120)

        return Response({"session": message_provider.session})


__all__ = ["SendAuthVerificationCodeView"]
