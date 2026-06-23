from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.assessment.services.monthly_assessment import MonthlyAssessmentService

from .serializers import MonthlyAssessmentListSerializer


class MonthlyAssessmentListAPIView(ListAPIView):
    serializer_class = MonthlyAssessmentListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        assessments = MonthlyAssessmentService(request.user).get_assessments()
        serializer = self.get_serializer(assessments, many=True)
        return Response(serializer.data)


__all__ = ["MonthlyAssessmentListAPIView"]
