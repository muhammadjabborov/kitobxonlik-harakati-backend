from adrf.views import APIView
from asgiref.sync import sync_to_async
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from django.db.transaction import non_atomic_requests

from apps.users.api_endpoints.auth.CheckPhoneNumber.serializers import (
    CheckPhoneNumberSerializer,
)
from apps.users.models import User


class CheckPhoneNumberView(APIView):
    serializer_class = CheckPhoneNumberSerializer

    @non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(request_body=CheckPhoneNumberSerializer)
    async def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        phone_number = str(serializer.validated_data["phone_number"])

        registered = await User.objects.filter(phone_number=phone_number).aexists()
        return Response({"registered": registered})


__all__ = ["CheckPhoneNumberView"]
