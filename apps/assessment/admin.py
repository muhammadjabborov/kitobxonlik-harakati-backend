from django.contrib import admin

from apps.assessment.models import (
    AssessmentQuestion,
    AssessmentQuestionDistribution,
    MonthlyAssessment,
    QuestionOption,
    UserMonthlyAssessmentAttempt,
    UserQuestionAnswer,
)


class AssessmentQuestionDistributionInline(admin.TabularInline):
    model = AssessmentQuestionDistribution
    extra = 0
    fields = ("question_type", "question_count")


@admin.register(MonthlyAssessment)
class MonthlyAssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "start_time", "end_time", "time_limit")
    list_display_links = ("id", "__str__")
    list_filter = ("month_grade__grade", "month_grade__month__season")
    search_fields = ("month_grade__month__season__title",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [AssessmentQuestionDistributionInline]


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    fields = ("option_text", "is_correct")


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "monthly_assessment", "question_type", "is_active")
    list_display_links = ("id", "__str__")
    list_filter = ("question_type", "monthly_assessment", "is_active")
    autocomplete_fields = ("monthly_assessment",)
    search_fields = ("question",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuestionOptionInline]


class UserQuestionAnswerInline(admin.TabularInline):
    model = UserQuestionAnswer
    extra = 0
    fields = (
        "id",
        "order",
        "question",
        "selected_option",
        "submitted_answer",
        "is_submitted",
        "is_correct",
    )
    can_delete = False
    ordering = ("order",)


@admin.register(UserMonthlyAssessmentAttempt)
class UserMonthlyAssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "monthly_assessment",
        "is_completed",
        "total_score",
        "spent_time_ms",
        "started_at",
        "finished_at",
    )
    list_display_links = ("id", "user", "monthly_assessment")
    list_filter = ("is_completed", "monthly_assessment__month_grade__grade")
    search_fields = ("user__full_name", "user__phone_number")
    autocomplete_fields = ("user", "monthly_assessment")
    readonly_fields = (
        "started_at",
        "finished_at",
        "spent_time_ms",
        "total_score",
        "created_at",
        "updated_at",
    )
    inlines = [UserQuestionAnswerInline]
