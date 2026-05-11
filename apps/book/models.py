from admin_async_upload.models import AsyncFileField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.users.choices import GradeChoices


class Author(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    image = models.ImageField(
        upload_to="authors/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Image"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def __str__(self):
        return self.name


class Category(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    order = models.PositiveSmallIntegerField(verbose_name=_("Order"), default=0)

    class Meta:
        ordering = ("order",)
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title


class Language(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    code = models.CharField(max_length=15, verbose_name=_("Code"), unique=True)

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return self.name


class Book(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(max_length=255, verbose_name=_("Slug"), unique=True, null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"))
    image = models.ImageField(
        upload_to="books/covers/%Y/%m/",
        verbose_name=_("Cover Image"),
        max_length=255,
    )
    authors = models.ManyToManyField(Author, verbose_name=_("Authors"), related_name="books")
    categories = models.ManyToManyField(Category, verbose_name=_("Categories"), related_name="books")
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Language"),
        related_name="books",
    )
    published_year = models.PositiveIntegerField(verbose_name=_("Published Year"), null=True, blank=True)
    page_count = models.PositiveIntegerField(verbose_name=_("Page Count"), null=True, blank=True)
    epub_file = models.FileField(
        upload_to="books/epub/%Y/%m/",
        verbose_name=_("EPUB File"),
        max_length=255,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["epub"])],
    )
    grades = models.CharField(
        max_length=8,
        choices=GradeChoices.choices,
        verbose_name=_("Grade"),
        null=True,
        blank=True,
    )
    featured_date = models.DateField(
        verbose_name=_("Featured Date"),
        null=True,
        blank=True,
        help_text=_("Set to the 1st of the month (e.g. 2026-06-01 for June 2026)"),
    )
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["published_year"]),
            models.Index(fields=["featured_date"]),
            models.Index(fields=["grades"]),
        ]

    def __str__(self):
        author_names = ", ".join(a.name for a in self.authors.all())
        if author_names:
            return f"{self.title} — {author_names}"
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title, allow_unicode=False)
            if not base_slug:
                base_slug = f"book-{self.pk or 'new'}"
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def audio_duration(self):
        """Total audio duration in seconds across all chapters."""
        result = self.audio_files.aggregate(total=models.Sum("duration"))
        return result["total"] or 0

    @property
    def has_audiobook(self):
        return self.audio_files.exists()

    @property
    def has_ebook(self):
        return bool(self.epub_file)


class AudioFile(BaseModel):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name=_("Book"),
        related_name="audio_files",
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    file = AsyncFileField(
        upload_to="books/audio/%Y/%m/",
        verbose_name=_("MP3 File"),
        max_length=511,
        validators=[FileExtensionValidator(allowed_extensions=["mp3"])],
    )
    duration = models.PositiveIntegerField(verbose_name=_("Duration (seconds)"), default=0)
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)

    class Meta:
        ordering = ("order",)
        verbose_name = _("Audio File")
        verbose_name_plural = _("Audio Files")

    def __str__(self):
        return f"{self.book.title} — {self.title}"
