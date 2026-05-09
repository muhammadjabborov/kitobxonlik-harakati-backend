from django.db import models
from django.utils.translation import gettext_lazy as _


class GradeChoices(models.TextChoices):
    GRADE_1_5 = "1_5", _("1-5 sinf")
    GRADE_6 = "6", _("6-sinf")
    GRADE_7 = "7", _("7-sinf")
    GRADE_8 = "8", _("8-sinf")
    GRADE_9 = "9", _("9-sinf")
    GRADE_10 = "10", _("10-sinf")
    GRADE_11 = "11", _("11-sinf")


class IdentityTypeChoices(models.TextChoices):
    PASSPORT = "passport", _("Passport")
    METRIC = "metric", _("Metric")
