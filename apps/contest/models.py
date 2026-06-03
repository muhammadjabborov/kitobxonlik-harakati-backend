from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.users.choices import GradeChoices


class MonthlyTest(BaseModel):
    """
    One test per month per grade, covering one or more books.
    Example: March 2026 | Grade 6 | ["O'tkan Kunlar", "Sariq Devni Minib"]
    """

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    books = models.ManyToManyField(
        "book.Book",
        verbose_name=_("Books"),
        blank=True,
        related_name="monthly_tests",
    )
    grade = models.CharField(
        verbose_name=_("Grade"),
        max_length=10,
        choices=GradeChoices.choices,
        db_index=True,
    )
    month = models.PositiveIntegerField(
        verbose_name=_("Month"),
        help_text=_("1 = January … 12 = December"),
    )
    year = models.PositiveIntegerField(verbose_name=_("Year"))
    start_time = models.DateTimeField(verbose_name=_("Start time"))
    end_time = models.DateTimeField(verbose_name=_("End time"))
    time_limit = models.PositiveIntegerField(
        verbose_name=_("Time limit (seconds)"),
        help_text=_("Seconds allowed to complete the test"),
    )
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True, db_index=True)

    class Meta:
        verbose_name = _("Monthly test")
        verbose_name_plural = _("Monthly tests")
        constraints = [
            models.UniqueConstraint(
                fields=["grade", "month", "year"],
                name="unique_monthly_test_grade_month_year",
            ),
        ]
        indexes = [
            models.Index(fields=["month", "year"], name="monthly_test_month_year_idx"),
            models.Index(fields=["start_time", "end_time"], name="monthly_test_time_range_idx"),
        ]

    def __str__(self):
        return f"{self.title} | {self.get_grade_display()} | {self.month}/{self.year}"


# =================== Multiple Choice Question (A, B, C, D) =================== #


class MultipleChoiceQuestion(BaseModel):
    test = models.ForeignKey(
        MonthlyTest,
        verbose_name=_("Test"),
        on_delete=models.CASCADE,
        related_name="mc_questions",
    )
    question = models.TextField(verbose_name=_("Question"))
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    class Meta:
        verbose_name = _("Multiple choice question")
        verbose_name_plural = _("Multiple choice questions")
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["test", "order"],
                name="unique_mc_question_test_order",
            ),
        ]
        indexes = [
            models.Index(fields=["test", "is_active"], name="mc_question_test_active_idx"),
        ]

    def __str__(self):
        return f"[MC] {self.question[:80]}"


class MultipleChoiceQuestionOption(BaseModel):
    """A, B, C, D options for a multiple choice question."""

    question = models.ForeignKey(
        MultipleChoiceQuestion,
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
        related_name="options",
    )
    label = models.CharField(
        verbose_name=_("Label"),
        max_length=5,
        help_text=_("A, B, C or D"),
    )
    content = models.CharField(verbose_name=_("Content"), max_length=512)
    is_correct = models.BooleanField(verbose_name=_("Is correct"), default=False)

    class Meta:
        verbose_name = _("Multiple choice question option")
        verbose_name_plural = _("Multiple choice question options")
        ordering = ["label"]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "label"],
                name="unique_mc_option_question_label",
            ),
        ]
        indexes = [
            models.Index(fields=["question", "is_correct"], name="mc_option_correct_idx"),
        ]

    def __str__(self):
        return f"{self.label}: {self.content}"


# =================== Short Answer Question (written) =================== #


class ShortAnswerQuestion(BaseModel):
    test = models.ForeignKey(
        MonthlyTest,
        verbose_name=_("Test"),
        on_delete=models.CASCADE,
        related_name="sa_questions",
    )
    question = models.TextField(verbose_name=_("Question"))
    answer = models.CharField(
        verbose_name=_("Correct answer"),
        max_length=512,
        help_text=_("Expected correct answer text"),
    )
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    class Meta:
        verbose_name = _("Short answer question")
        verbose_name_plural = _("Short answer questions")
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["test", "order"],
                name="unique_sa_question_test_order",
            ),
        ]
        indexes = [
            models.Index(fields=["test", "is_active"], name="sa_question_test_active_idx"),
        ]

    def __str__(self):
        return f"[SA] {self.question[:80]}"


# =================== User Participation =================== #


class UserMonthlyTestParticipation(BaseModel):
    """Tracks a single user's attempt at a monthly test."""

    test = models.ForeignKey(
        MonthlyTest,
        verbose_name=_("Test"),
        on_delete=models.CASCADE,
        related_name="participations",
    )
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="monthly_test_participations",
    )
    # created_at (from BaseModel) acts as the participation start timestamp
    finished_at = models.DateTimeField(verbose_name=_("Finished at"), null=True, blank=True)
    spent_time = models.PositiveIntegerField(
        verbose_name=_("Spent time (seconds)"),
        default=0,
        help_text=_("Actual seconds the user spent before submitting"),
    )
    is_completed = models.BooleanField(verbose_name=_("Is completed"), default=False)
    mc_correct = models.PositiveIntegerField(verbose_name=_("MC correct answers"), default=0)
    sa_correct = models.PositiveIntegerField(verbose_name=_("SA correct answers"), default=0)
    total_score = models.DecimalField(
        verbose_name=_("Total score (percent)"),
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = _("User monthly test participation")
        verbose_name_plural = _("User monthly test participations")
        constraints = [
            models.UniqueConstraint(
                fields=["test", "user"],
                name="unique_participation_test_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "is_completed"], name="participation_user_done_idx"),
            models.Index(fields=["test", "is_completed"], name="participation_test_done_idx"),
            models.Index(fields=["total_score"], name="participation_score_idx"),
        ]

    def __str__(self):
        return f"{self.user} | {self.test}"


class UserMultipleChoiceAnswer(BaseModel):
    """User's selected option for a multiple choice question."""

    participation = models.ForeignKey(
        UserMonthlyTestParticipation,
        verbose_name=_("Participation"),
        on_delete=models.CASCADE,
        related_name="mc_answers",
    )
    question = models.ForeignKey(
        MultipleChoiceQuestion,
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    selected_option = models.ForeignKey(
        MultipleChoiceQuestionOption,
        verbose_name=_("Selected option"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_answers",
    )
    is_correct = models.BooleanField(verbose_name=_("Is correct"), default=False)

    class Meta:
        verbose_name = _("User MC answer")
        verbose_name_plural = _("User MC answers")
        constraints = [
            models.UniqueConstraint(
                fields=["participation", "question"],
                name="unique_mc_answer_participation_question",
            ),
        ]
        indexes = [
            models.Index(fields=["participation", "is_correct"], name="mc_answer_correct_idx"),
        ]

    def __str__(self):
        return f"{self.participation.user} | {self.question}"


class UserShortAnswer(BaseModel):
    """User's written answer for a short answer question."""

    participation = models.ForeignKey(
        UserMonthlyTestParticipation,
        verbose_name=_("Participation"),
        on_delete=models.CASCADE,
        related_name="sa_answers",
    )
    question = models.ForeignKey(
        ShortAnswerQuestion,
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    user_answer = models.CharField(verbose_name=_("User answer"), max_length=512)
    is_correct = models.BooleanField(verbose_name=_("Is correct"), default=False)

    class Meta:
        verbose_name = _("User SA answer")
        verbose_name_plural = _("User SA answers")
        constraints = [
            models.UniqueConstraint(
                fields=["participation", "question"],
                name="unique_sa_answer_participation_question",
            ),
        ]
        indexes = [
            models.Index(fields=["participation", "is_correct"], name="sa_answer_correct_idx"),
        ]

    def __str__(self):
        return f"{self.participation.user} | {self.question}"
