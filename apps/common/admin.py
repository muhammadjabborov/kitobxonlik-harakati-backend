from django.contrib import admin

from . import models

@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "region", "created_at", "updated_at")
    list_display_links = ("id", "name")
    list_filter = ("region",)
    search_fields = ("name", "region__name")
    autocomplete_fields = ("region",)

@admin.register(models.Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district", "created_at", "updated_at")
    list_display_links = ("id", "name")
    list_filter = ("district",)
    search_fields = ("name", "district__name")
    autocomplete_fields = ("district",)


@admin.register(models.School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district", "created_at", "updated_at")
    list_display_links = ("id", "name")
    list_filter = ("district",)
    search_fields = ("name", "district__name")
    autocomplete_fields = ("district",)