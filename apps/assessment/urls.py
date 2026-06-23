from django.urls import path

from .api_endpoints import assessment_attempt, main

app_name = "assessment"

urlpatterns = [
    path(
        "MonthlyAssessmentList/",
        main.MonthlyAssessmentListAPIView.as_view(),
        name="MonthlyAssessmentList",
    ),
    path(
        "StartAssessment/<int:assessment_id>/",
        assessment_attempt.StartAssessmentAPIView.as_view(),
        name="StartAssessment",
    ),
    path(
        "ReenterAssessment/<int:attempt_id>/",
        assessment_attempt.ReenterAssessmentAPIView.as_view(),
        name="ReenterAssessment",
    ),
    path(
        "SubmitAssessment/<int:attempt_id>/",
        assessment_attempt.SubmitAssessmentAPIView.as_view(),
        name="SubmitAssessment",
    ),
]
