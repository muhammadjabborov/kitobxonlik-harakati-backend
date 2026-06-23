from django.core.cache import cache
from django.db.models import F

from apps.assessment.models import MonthlyAssessment, UserMonthlyAssessmentAttempt

ASSESSMENTS_CACHE_TIMEOUT = 60 * 10  # 10 minutes


class MonthlyAssessmentService:
    def __init__(self, user):
        self.user = user

    def get_assessments(self):
        assessments = self._get_cached_assessments()
        self._attach_attempt_data(assessments)
        return assessments

    def _get_cached_assessments(self):
        cache_key = f"monthly_assessments:{self.user.grade}"
        assessments = cache.get(cache_key)
        if not assessments:
            assessments = list(
                MonthlyAssessment.objects.filter(
                    month_grade__month__season__is_active=True,
                    month_grade__grade=self.user.grade,
                )
                .select_related("month_grade__month__season")
                .annotate(
                    month_start=F("month_grade__month__month_start"),
                    grade=F("month_grade__grade"),
                )
                .order_by("month_start")
            )
            cache.set(cache_key, assessments, timeout=ASSESSMENTS_CACHE_TIMEOUT)
        return assessments

    def _attach_attempt_data(self, assessments):
        attempts = UserMonthlyAssessmentAttempt.objects.filter(
            user=self.user,
            monthly_assessment_id__in=[a.id for a in assessments],
        )

        attempts_map = {attempt.monthly_assessment_id: attempt for attempt in attempts}

        for assessment in assessments:
            assessment.attempt = attempts_map.get(assessment.id)
