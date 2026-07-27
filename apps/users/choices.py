from django.db import models
from django.utils.translation import gettext_lazy as _


class CompetitionGradeGroupChoices(models.TextChoices):
    GROUP_1_5 = "1_5", _("1-5 sinf")
    GROUP_6_8 = "6_8", _("6-8 sinf")
    GROUP_9_11 = "9_11", _("9-11 sinf")


class IdentityTypeChoices(models.TextChoices):
    PASSPORT = "passport", _("Passport")
    METRIC = "metric", _("Metric")
