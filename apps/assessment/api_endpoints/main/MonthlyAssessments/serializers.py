from django.utils import timezone
from rest_framework import serializers

from apps.assessment.models import MonthlyAssessment, UserMonthlyAssessmentAttempt


class AssessmentStatus:
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    AVAILABLE = "available"
    LOCKED = "locked"


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMonthlyAssessmentAttempt
        fields = (
            "id",
            "total_score",
            "spent_time_ms",
        )


class MonthlyAssessmentListSerializer(serializers.ModelSerializer):
    month_start = serializers.DateField()
    grade = serializers.CharField()
    attempt = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyAssessment
        fields = (
            "id",
            "grade",
            "month_start",
            "start_time",
            "end_time",
            "time_limit",
            "attempt",
            "status",
        )

    def get_attempt(self, obj):
        if obj.attempt is None:
            return None
        return AttemptSerializer(obj.attempt).data

    def get_status(self, obj):
        if obj.attempt is not None:
            if obj.attempt.is_completed:
                return AssessmentStatus.COMPLETED
            return AssessmentStatus.IN_PROGRESS
        today = timezone.localdate()
        if obj.month_start <= today:
            return AssessmentStatus.AVAILABLE
        return AssessmentStatus.LOCKED
