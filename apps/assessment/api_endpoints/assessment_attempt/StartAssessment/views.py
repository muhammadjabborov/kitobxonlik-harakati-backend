from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assessment.models import MonthlyAssessment, UserMonthlyAssessmentAttempt
from apps.assessment.serializers import AssessmentAttemptDetailSerializer
from apps.assessment.services.assessment_attempt import AssessmentAttemptService


class StartAssessmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assessment_id):
        assessment = get_object_or_404(
            MonthlyAssessment.objects.select_related("month_grade__month"),
            id=assessment_id,
            month_grade__grade=request.user.grade,
            month_grade__month__season__is_active=True,
        )

        if assessment.month_grade.month.month_start > timezone.localdate():
            raise ValidationError(
                code="not_available",
                detail={"assessment": _("This assessment is not available yet.")},
            )

        if UserMonthlyAssessmentAttempt.objects.filter(
            user=request.user, monthly_assessment=assessment
        ).exists():
            raise ValidationError(
                code="already_exists",
                detail={
                    "assessment_attempt": _(
                        "An attempt for this assessment already exists."
                    )
                },
            )

        attempt = AssessmentAttemptService(request.user).start(assessment)
        return Response(
            AssessmentAttemptDetailSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )


__all__ = ["StartAssessmentView"]
