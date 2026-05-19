from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from . import models


@admin.register(models.Region)
class RegionAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "soato", "level")
    list_display_links = ("indented_title",)
    list_filter = ("level",)
    search_fields = ("name", "soato")


@admin.register(models.School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district", "created_at", "updated_at")
    list_display_links = ("id", "name")
    list_filter = ("district",)
    search_fields = ("name", "district__name")
    autocomplete_fields = ("district",)
