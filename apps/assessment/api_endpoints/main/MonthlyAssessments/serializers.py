from django.utils import timezone
from rest_framework import serializers

from apps.assessment.models import MonthlyAssessment


class AssessmentStatus:
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    AVAILABLE = "available"
    LOCKED = "locked"


class MonthlyAssessmentListSerializer(serializers.ModelSerializer):
    month_start = serializers.DateField()
    grade = serializers.CharField()
    attempt_id = serializers.IntegerField(allow_null=True, required=False)
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
            "attempt_id",
            "status",
        )

    def get_status(self, obj):
        if obj.attempt_id is not None:
            if obj.attempt_is_completed:
                return AssessmentStatus.COMPLETED
            return AssessmentStatus.IN_PROGRESS
        today = timezone.localdate()
        if obj.month_start <= today:
            return AssessmentStatus.AVAILABLE
        return AssessmentStatus.LOCKED
