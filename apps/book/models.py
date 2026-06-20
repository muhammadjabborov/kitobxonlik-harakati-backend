from admin_async_upload.models import AsyncFileField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Author(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    image = models.ImageField(
        upload_to="authors/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Image"),
        max_length=255,
    )
    mutolaa_id = models.CharField(
        max_length=255, verbose_name=_("Mutolaa ID"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def __str__(self):
        return self.name


class Genre(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    mutolaa_id = models.CharField(
        max_length=255, verbose_name=_("Mutolaa ID"), null=True, blank=True
    )
    order = models.PositiveSmallIntegerField(verbose_name=_("Order"), default=0)

    class Meta:
        ordering = ("order",)
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.title


class Book(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(
        max_length=255, verbose_name=_("Slug"), unique=True, null=True, blank=True
    )
    description = models.TextField(verbose_name=_("Description"))
    image = models.ImageField(
        upload_to="books/covers/%Y/%m/",
        verbose_name=_("Cover Image"),
        max_length=255,
    )
    authors = models.ManyToManyField(
        Author, verbose_name=_("Authors"), related_name="books"
    )
    genres = models.ManyToManyField(
        Genre, verbose_name=_("Genres"), related_name="books"
    )
    epub_file = models.FileField(
        upload_to="books/epub/%Y/%m/",
        verbose_name=_("EPUB File"),
        max_length=255,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["epub"])],
    )
    audiobook_duration = models.FloatField(
        verbose_name=_("Audiobook Duration"), null=True, blank=True
    )
    mutolaa_id = models.CharField(
        max_length=255, verbose_name=_("Mutolaa ID"), null=True, blank=True
    )
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

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
    duration = models.FloatField(
        verbose_name=_("Duration (seconds)"),
        null=True,
    )
    order = models.PositiveIntegerField(verbose_name=_("Order"), default=0)

    class Meta:
        ordering = ("order",)
        verbose_name = _("Audio File")
        verbose_name_plural = _("Audio Files")

    def __str__(self):
        return f"{self.book.title} — {self.title}"


class PlanToRead(BaseModel):
    book = models.ForeignKey(
        "book.Book", on_delete=models.CASCADE, verbose_name=_("Book")
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name=_("User")
    )

    class Meta:
        verbose_name = _("Plan To Read")
        verbose_name_plural = _("Plan To Reads")
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user} - {self.book}"
