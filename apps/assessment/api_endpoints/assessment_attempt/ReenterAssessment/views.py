from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessment.models import UserMonthlyAssessmentAttempt
from apps.assessment.serializers import AssessmentAttemptDetailSerializer
from apps.assessment.services.assessment_attempt import AssessmentAttemptService


class ReenterAssessmentAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, attempt_id):
        attempt = get_object_or_404(
            UserMonthlyAssessmentAttempt,
            id=attempt_id,
            user=request.user,
            is_completed=False,
        )
        attempt = AssessmentAttemptService(request.user).get_attempt_with_questions(
            attempt
        )
        return Response(AssessmentAttemptDetailSerializer(attempt).data)


__all__ = ["ReenterAssessmentAPIView"]
