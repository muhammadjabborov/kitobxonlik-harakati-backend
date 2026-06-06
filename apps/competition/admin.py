from django.contrib import admin

from apps.competition.models import (
    CompetitionMonth,
    CompetitionMonthGrade,
    CompetitionSeason,
)


@admin.register(CompetitionSeason)
class CompetitionSeasonAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "created_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")


class CompetitionMonthGradeInline(admin.StackedInline):
    model = CompetitionMonthGrade
    extra = 0
    fields = ("grade", "books")
    filter_horizontal = ("books",)
    show_change_link = True


@admin.register(CompetitionMonth)
class CompetitionMonthAdmin(admin.ModelAdmin):
    list_display = ("__str__", "season", "month_start", "is_active")
    list_editable = ("is_active",)
    list_filter = ("season", "is_active")
    search_fields = ("season__title",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [CompetitionMonthGradeInline]


@admin.register(CompetitionMonthGrade)
class CompetitionMonthGradeAdmin(admin.ModelAdmin):
    list_display = ("__str__", "month", "grade")
    list_filter = ("grade", "month__season")
    search_fields = ("month__season__title",)
    filter_horizontal = ("books",)
    readonly_fields = ("created_at", "updated_at")
