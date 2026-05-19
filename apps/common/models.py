from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class Region(BaseModel):
    name = models.CharField(_("Name"), max_length=128, unique=True)

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    def __str__(self):
        return self.name


class District(BaseModel):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name=_("Region"),
    )
    name = models.CharField(_("Name"), max_length=128)

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")
        unique_together = ("region", "name")

    def __str__(self):
        return f"{self.region} — {self.name}"

class Neighborhood(BaseModel):
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="neighborhoods",
        verbose_name=_("District"),
    )
    name = models.CharField(_("Name"), max_length=128)
    
    class Meta:
        verbose_name = _("Neighborhood")
        verbose_name_plural = _("Neighborhoods")
        unique_together = ("district", "name")

    def __str__(self):
        return f"{self.district} — {self.name}"

class School(BaseModel):
    name = models.CharField(_("Name"), max_length=128)
    district = models.ForeignKey(
        District,
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
