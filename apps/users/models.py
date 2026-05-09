from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel, Region
from apps.users.choices import GradeChoices, IdentityTypeChoices
from apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    full_name = models.CharField(_("Full name"), max_length=256)
    phone_number = models.CharField(_("Phone number"), max_length=20, unique=True)
    age = models.PositiveSmallIntegerField(_("Age"), null=True, blank=True)
    grade = models.CharField(
        _("Grade"),
        max_length=8,
        choices=GradeChoices.choices,
        null=True,
        blank=True,
    )
    school_number = models.PositiveSmallIntegerField(
        _("School number"),
        null=True,
        blank=True,
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        related_name="users",
        verbose_name=_("Region"),
        null=True,
        blank=True,
    )
    identity_type = models.CharField(
        _("Identity type"),
        max_length=16,
        choices=IdentityTypeChoices.choices,
        null=True,
        blank=True,
    )
    identity_number = models.CharField(
        _("Identity number"),
        max_length=64,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(_("Active"), default=True)
    is_staff = models.BooleanField(_("Staff"), default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["grade"], name="user_grade_idx"),
            models.Index(fields=["identity_number"], name="user_identity_number_idx"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
