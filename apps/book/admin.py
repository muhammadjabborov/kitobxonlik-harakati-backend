from django.contrib import admin

from apps.book.models import AudioFile, Author, Book, Genre, PlanToRead


class AudioFileInline(admin.StackedInline):
    model = AudioFile
    extra = 0
    fields = ("order", "title", "file", "duration")
    ordering = ("order",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "mutolaa_id",
        "is_active",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active", "genres", "mutolaa_id")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("authors", "genres")
    inlines = [AudioFileInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(PlanToRead)
class PlanToReadAdmin(admin.ModelAdmin):
    list_filter = ["book"]
    autocomplete_fields = ["user", "book"]
    search_fields = ("user__full_name", "book__title")
    list_per_page = 10
