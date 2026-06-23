from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessment.models import UserMonthlyAssessmentAttempt
from apps.assessment.services.assessment_attempt import AssessmentAttemptService

from .serializers import SubmitAttemptSerializer, SubmitResultSerializer


class SubmitAssessmentAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        request_body=SubmitAttemptSerializer,
        responses={200: SubmitResultSerializer},
    )
    def post(self, request, attempt_id):
        attempt = get_object_or_404(
            UserMonthlyAssessmentAttempt,
            id=attempt_id,
            user=request.user,
            is_completed=False,
        )
        serializer = SubmitAttemptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attempt = AssessmentAttemptService(request.user).submit(
            attempt=attempt,
            answers_data=serializer.validated_data["answers"],
        )
        return Response(SubmitResultSerializer(attempt).data)


__all__ = ["SubmitAssessmentAPIView"]
