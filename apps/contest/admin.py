from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.contest.models import (
    MonthlyTest,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionOption,
    ShortAnswerQuestion,
    UserMonthlyTestParticipation,
    UserMultipleChoiceAnswer,
    UserShortAnswer,
)


class MultipleChoiceQuestionOptionInline(admin.TabularInline):
    model = MultipleChoiceQuestionOption
    extra = 4
    fields = ("label", "content", "is_correct")
    ordering = ("label",)


class MultipleChoiceQuestionInline(admin.TabularInline):
    model = MultipleChoiceQuestion
    extra = 0
    fields = ("order", "question", "is_active")
    ordering = ("order",)
    show_change_link = True


class ShortAnswerQuestionInline(admin.TabularInline):
    model = ShortAnswerQuestion
    extra = 0
    fields = ("order", "question", "answer", "is_active")
    ordering = ("order",)
    show_change_link = True


@admin.register(MonthlyTest)
class MonthlyTestAdmin(admin.ModelAdmin):
    list_display = ("title", "grade", "month", "year", "start_time", "end_time", "is_active")
    list_editable = ("is_active",)
    list_filter = ("grade", "year", "month", "is_active")
    search_fields = ("title",)
    filter_horizontal = ("books",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [MultipleChoiceQuestionInline, ShortAnswerQuestionInline]
    fieldsets = (
        (None, {
            "fields": ("title", "books", "grade", "month", "year", "is_active"),
        }),
        (_("Schedule"), {
            "fields": ("start_time", "end_time", "time_limit"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "test", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("test", "is_active")
    search_fields = ("question",)
    autocomplete_fields = ("test",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [MultipleChoiceQuestionOptionInline]


@admin.register(ShortAnswerQuestion)
class ShortAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "test", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("test", "is_active")
    search_fields = ("question",)
    autocomplete_fields = ("test",)
    readonly_fields = ("created_at", "updated_at")


class UserMultipleChoiceAnswerInline(admin.TabularInline):
    model = UserMultipleChoiceAnswer
    extra = 0
    fields = ("question", "selected_option", "is_correct")
    readonly_fields = ("question", "selected_option", "is_correct")
    can_delete = False


class UserShortAnswerInline(admin.TabularInline):
    model = UserShortAnswer
    extra = 0
    fields = ("question", "user_answer", "is_correct")
    readonly_fields = ("question", "user_answer", "is_correct")
    can_delete = False


@admin.register(UserMonthlyTestParticipation)
class UserMonthlyTestParticipationAdmin(admin.ModelAdmin):
    list_display = (
        "user", "test", "is_completed", "mc_correct", "sa_correct",
        "total_score", "spent_time", "finished_at",
    )
    list_filter = ("is_completed", "test__grade", "test__year", "test__month")
    search_fields = ("user__full_name", "user__phone_number", "test__title")
    autocomplete_fields = ("user", "test")
    readonly_fields = ("created_at", "updated_at", "finished_at", "spent_time", "mc_correct", "sa_correct", "total_score")
    inlines = [UserMultipleChoiceAnswerInline, UserShortAnswerInline]
    fieldsets = (
        (None, {
            "fields": ("user", "test", "is_completed"),
        }),
        (_("Results"), {
            "fields": ("mc_correct", "sa_correct", "total_score", "spent_time", "finished_at"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
