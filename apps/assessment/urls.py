from django.urls import path

from .api_endpoints import assessment_attempt, main

app_name = "assessment"

urlpatterns = [
    path(
        "MonthlyAssessmentList/",
        main.MonthlyAssessmentListView.as_view(),
        name="MonthlyAssessmentList",
    ),
    path(
        "StartAssessment/<int:assessment_id>/",
        assessment_attempt.StartAssessmentView.as_view(),
        name="StartAssessment",
    ),
    path(
        "ReenterAssessment/<int:attempt_id>/",
        assessment_attempt.ReenterAssessmentView.as_view(),
        name="ReenterAssessment",
    ),
    path(
        "SubmitAssessment/<int:attempt_id>/",
        assessment_attempt.SubmitAssessmentView.as_view(),
        name="SubmitAssessment",
    ),
]
