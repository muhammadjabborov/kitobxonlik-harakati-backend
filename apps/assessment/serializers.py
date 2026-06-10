from rest_framework import serializers

from apps.assessment.models import (
    QuestionOption,
    UserMonthlyAssessmentAttempt,
    UserQuestionAnswer,
)


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ("id", "option_text")


class AttemptQuestionSerializer(serializers.ModelSerializer):
    user_question_id = serializers.IntegerField(source="id")
    question_type = serializers.CharField(source="question.question_type")
    question_text = serializers.CharField(source="question.question")
    question_options = QuestionOptionSerializer(source="question.options", many=True)

    class Meta:
        model = UserQuestionAnswer
        fields = (
            "user_question_id",
            "question_type",
            "question_text",
            "question_options",
        )


class AssessmentAttemptDetailSerializer(serializers.ModelSerializer):
    time_limit = serializers.IntegerField(source="monthly_assessment.time_limit")
    user_questions = AttemptQuestionSerializer(
        source="user_question_answers", many=True
    )

    class Meta:
        model = UserMonthlyAssessmentAttempt
        fields = ("id", "started_at", "time_limit", "user_questions")
