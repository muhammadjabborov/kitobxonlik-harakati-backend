from rest_framework import serializers

from apps.assessment.models import UserMonthlyAssessmentAttempt


class SubmitAnswerSerializer(serializers.Serializer):
    user_question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField(required=False, allow_null=True)
    submitted_answer = serializers.CharField(required=False, allow_blank=True)


class SubmitAttemptSerializer(serializers.Serializer):
    answers = SubmitAnswerSerializer(many=True)


class SubmitResultSerializer(serializers.ModelSerializer):
    correct_count = serializers.IntegerField()
    total_count = serializers.IntegerField()

    class Meta:
        model = UserMonthlyAssessmentAttempt
        fields = ("total_score", "correct_count", "total_count")
