from django.contrib import admin

from apps.book.models import AudioFile, Author, Book, Category, Language


class AudioFileInline(admin.TabularInline):
    model = AudioFile
    extra = 0
    fields = ("order", "title", "file", "duration")
    ordering = ("order",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title", "grades", "featured_date",
        "published_year", "language", "page_count", "is_active", "order",
    )
    list_editable = ("is_active", "order")
    list_filter = ("is_active", "language", "categories", "grades", "featured_date")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("authors", "categories")
    inlines = [AudioFileInline]
    readonly_fields = ("created_at", "updated_at")
