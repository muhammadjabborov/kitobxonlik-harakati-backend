from django.db import models
from django.utils.translation import gettext_lazy as _


class QuestionTypeChoices(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", _("Multiple choice")
    SHORT_ANSWER = "short_answer", _("Short answer")
