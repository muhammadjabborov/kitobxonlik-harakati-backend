from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.assessment.enums import QuestionTypeChoices
from apps.common.models import BaseModel


class MonthlyAssessment(BaseModel):
    month_grade = models.OneToOneField(
        "competition.CompetitionMonthGrade",
        verbose_name=_("Month grade"),
        on_delete=models.CASCADE,
        related_name="monthly_assessment",
    )
    start_time = models.DateTimeField(verbose_name=_("Start time"))
    end_time = models.DateTimeField(verbose_name=_("End time"))
    time_limit = models.PositiveIntegerField(
        verbose_name=_("Time limit (seconds)"),
        help_text=_("Seconds allowed to complete the test"),
    )

    class Meta:
        verbose_name = _("Monthly assessment")
        verbose_name_plural = _("Monthly assessments")

    def __str__(self):
        return str(self.month_grade)


class AssessmentQuestionDistribution(BaseModel):
    monthly_assessment = models.ForeignKey(
        MonthlyAssessment,
        verbose_name=_("Monthly assessment"),
        on_delete=models.CASCADE,
        related_name="question_distributions",
    )
    question_type = models.CharField(
        verbose_name=_("Question type"),
        max_length=32,
        choices=QuestionTypeChoices.choices,
    )
    question_count = models.PositiveIntegerField(
        verbose_name=_("Question count"),
        help_text=_("How many questions of this type to pick randomly for each user"),
    )

    class Meta:
        verbose_name = _("Assessment question distribution")
        verbose_name_plural = _("Assessment question distributions")
        constraints = [
            models.UniqueConstraint(
                fields=["monthly_assessment", "question_type"],
                name="unique_assessment_question_type_distribution",
            ),
        ]

    def __str__(self):
        return f"{self.monthly_assessment} — {self.get_question_type_display()} x{self.question_count}"


# ================== User Attempt ================== #
class UserMonthlyAssessmentAttempt(BaseModel):
    monthly_assessment = models.ForeignKey(
        MonthlyAssessment,
        verbose_name=_("Monthly assessment"),
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="monthly_assessment_attempts",
    )
    started_at = models.DateTimeField(
        verbose_name=_("Started at"), default=timezone.now
    )
    finished_at = models.DateTimeField(
        verbose_name=_("Finished at"), null=True, blank=True
    )
    spent_time_ms = models.PositiveBigIntegerField(
        verbose_name=_("Spent time (milliseconds)"),
        default=0,
    )
    is_completed = models.BooleanField(verbose_name=_("Is completed"), default=False)
    total_score = models.DecimalField(
        verbose_name=_("Total score (percent)"),
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = _("User monthly assessment attempt")
        verbose_name_plural = _("User monthly assessment attempts")
        constraints = [
            models.UniqueConstraint(
                fields=["monthly_assessment", "user"],
                name="unique_attempt_assessment_user",
            ),
        ]

    def __str__(self):
        return f"{self.user} | {self.monthly_assessment}"


# ================== Questions ================== #
class AssessmentQuestion(BaseModel):
    monthly_assessment = models.ForeignKey(
        MonthlyAssessment,
        verbose_name=_("Monthly assessment"),
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_type = models.CharField(
        verbose_name=_("Question type"),
        max_length=32,
        choices=QuestionTypeChoices.choices,
    )
    question = models.TextField(verbose_name=_("Question"))
    correct_answer = models.CharField(
        verbose_name=_("Correct answer"),
        max_length=512,
        blank=True,
        help_text=_("Used only for short answer questions"),
    )
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    class Meta:
        verbose_name = _("Assessment question")
        verbose_name_plural = _("Assessment questions")

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.question[:80]}"


class QuestionOption(BaseModel):
    question = models.ForeignKey(
        AssessmentQuestion,
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
        related_name="options",
    )
    option_text = models.CharField(verbose_name=_("Option text"), max_length=512)
    is_correct = models.BooleanField(verbose_name=_("Is correct"), default=False)

    class Meta:
        verbose_name = _("Question option")
        verbose_name_plural = _("Question options")
        constraints = [
            models.UniqueConstraint(
                fields=["question"],
                condition=models.Q(is_correct=True),
                name="unique_correct_option_per_question",
            ),
        ]

    def __str__(self):
        return f"{self.option_text[:60]} ({'correct' if self.is_correct else 'wrong'})"


class UserQuestionAnswer(BaseModel):
    attempt = models.ForeignKey(
        UserMonthlyAssessmentAttempt,
        verbose_name=_("Attempt"),
        on_delete=models.CASCADE,
        related_name="question_answers",
    )
    question = models.ForeignKey(
        AssessmentQuestion,
        verbose_name=_("Question"),
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    order = models.PositiveIntegerField(verbose_name=_("Order"))
    selected_option = models.ForeignKey(
        QuestionOption,
        verbose_name=_("Selected option"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_answers",
    )
    submitted_answer = models.CharField(
        verbose_name=_("Submitted answer"),
        max_length=512,
        blank=True,
    )
    is_submitted = models.BooleanField(
        verbose_name=_("Is submitted"),
        default=False,
        help_text=_("Whether user submitted the answer or not"),
    )
    is_correct = models.BooleanField(verbose_name=_("Is correct"), default=False)

    class Meta:
        verbose_name = _("User question answer")
        verbose_name_plural = _("User question answers")

    def __str__(self):
        return f"{self.attempt.user} | Q{self.order}"
