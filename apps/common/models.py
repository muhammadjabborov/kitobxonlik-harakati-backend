from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class Region(MPTTModel):
    name = models.CharField(_("Name"), max_length=255)
    soato = models.CharField(_("Soato"), max_length=255, unique=True, null=True, blank=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children", verbose_name=_("Parent")
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    def __str__(self):
        return self.name


class School(BaseModel):
    name = models.CharField(_("Name"), max_length=128)
    district = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="schools",
        verbose_name=_("District"),
    )

    class Meta:
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        unique_together = ("district", "name")

    def __str__(self):
        return f"{self.district} — {self.name}"
