from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "age",
        "grade",
        "region",
        "identity_type",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_display_links = ("id", "phone_number")
    list_filter = ("grade", "identity_type", "is_active", "is_staff", "region")
    search_fields = ("full_name", "phone_number", "identity_number")
    ordering = ("-created_at",)
    autocomplete_fields = ("region",)

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "full_name",
                    "age",
                    "grade",
                    "region",
                    "identity_type",
                    "identity_number",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "full_name",
                    "age",
                    "grade",
                    "region",
                    "identity_type",
                    "identity_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
