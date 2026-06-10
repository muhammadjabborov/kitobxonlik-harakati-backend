from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.users.choices import GradeChoices


class CompetitionSeason(BaseModel):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    year = models.PositiveIntegerField(verbose_name=_("Year"))
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    class Meta:
        verbose_name = _("Competition season")
        verbose_name_plural = _("Competition seasons")
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="only_one_active_competition_season",
            ),
        ]

    def __str__(self):
        return f"{self.title} | {self.year}"


class CompetitionMonth(BaseModel):
    season = models.ForeignKey(
        CompetitionSeason,
        verbose_name=_("Season"),
        on_delete=models.CASCADE,
        related_name="months",
    )
    month_start = models.DateField(verbose_name=_("Month start"))
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    class Meta:
        verbose_name = _("Competition month")
        verbose_name_plural = _("Competition months")
        constraints = [
            models.UniqueConstraint(
                fields=["season", "month_start"],
                name="unique_competition_month_season_month",
            ),
        ]

    def __str__(self):
        return f"{self.season} — {self.month_start}"


class CompetitionMonthGrade(BaseModel):
    month = models.ForeignKey(
        CompetitionMonth,
        verbose_name=_("Month"),
        on_delete=models.CASCADE,
        related_name="month_grades",
    )
    grade = models.CharField(
        verbose_name=_("Grade"),
        max_length=10,
        choices=GradeChoices.choices,
    )
    books = models.ManyToManyField(
        "book.Book",
        verbose_name=_("Books"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Competition month grade")
        verbose_name_plural = _("Competition month grades")
        constraints = [
            models.UniqueConstraint(
                fields=["month", "grade"],
                name="unique_competition_month_grade",
            ),
        ]

    def __str__(self):
        return f"{self.month} ({self.grade})"
