import logging
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from apps.book.models import AudioFile, Author, Book, Genre

logger = logging.getLogger(__name__)


class MutolaaBookSyncError(Exception):
    pass


@dataclass
class MutolaaBookSyncResult:
    book: Book
    created_authors: int = 0
    reused_authors: int = 0
    created_genres: int = 0
    reused_genres: int = 0
    created_audio_files: int = 0
    updated_fields: list[str] = field(default_factory=list)


class MutolaaBookSyncService:
    endpoint_path = "/api/v1/common/kitobxonlik-harakati/BookList/"

    def __init__(self, book: Book, log_callback=None):
        self.book = book
        self.config = settings.KITOBXONLIK_HARAKATI_CONFIG
        self.timeout = self.config.get("timeout", 30)
        self.log_callback = log_callback

    def sync(self) -> MutolaaBookSyncResult:
        self._log(
            f"Starting Mutolaa sync for local book id={self.book.pk}, "
            f"mutolaa_id={self.book.mutolaa_id}."
        )
        mutolaa_data = self._fetch_book_data()
        result = MutolaaBookSyncResult(book=self.book)

        with transaction.atomic():
            self.book = Book.objects.select_for_update().get(pk=self.book.pk)
            self._sync_book_fields(mutolaa_data, result)
            self._sync_authors(mutolaa_data.get("authors", []), result)
            self._sync_genres(mutolaa_data.get("categories", []), result)
            self._sync_audio_files(mutolaa_data.get("audiofiles", []), result)
            self.book.save()

        result.book = self.book
        self._log(
            f"Finished Mutolaa sync for local book id={self.book.pk}. "
            f"Audio files saved: {result.created_audio_files}."
        )
        return result

    def _fetch_book_data(self):
        mutolaa_id = self._get_mutolaa_id()
        self._log(f"Fetching Mutolaa book data for mutolaa_id={mutolaa_id}.")
        response_data = self._post_book_list([mutolaa_id])

        if not isinstance(response_data, list):
            raise MutolaaBookSyncError("Mutolaa response must be a list.")

        for item in response_data:
            if str(item.get("id")) == str(mutolaa_id):
                self._log(f"Mutolaa returned data for '{item.get('title')}'.")
                return item

        raise MutolaaBookSyncError(f"Mutolaa book was not found for id={mutolaa_id}.")

    def _post_book_list(self, book_ids):
        config = self._get_config()
        url = urljoin(
            config["base_url"].rstrip("/") + "/",
            self.endpoint_path.lstrip("/"),
        )
        self._log(f"Sending Mutolaa API request to {url}.")

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(
                    url,
                    json={"book_ids": book_ids},
                    auth=(config["username"], config["password"]),
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise MutolaaBookSyncError(
                f"Mutolaa API returned {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise MutolaaBookSyncError("Could not connect to Mutolaa API.") from exc
        except ValueError as exc:
            raise MutolaaBookSyncError("Mutolaa API returned invalid JSON.") from exc

    def _sync_book_fields(self, data, result):
        update_fields = []

        title = self._clean_value(data.get("title"))
        if title and self.book.title != title:
            self._log(
                f"Keeping existing book title '{self.book.title}'. "
                f"Mutolaa API title is '{title}'."
            )

        mutolaa_id = self._clean_mutolaa_id(data.get("id"))
        if mutolaa_id and self.book.mutolaa_id != mutolaa_id:
            self.book.mutolaa_id = mutolaa_id
            update_fields.append("mutolaa_id")

        audiobook_duration = data.get("audiobook_duration")
        if self.book.audiobook_duration != audiobook_duration:
            self.book.audiobook_duration = audiobook_duration
            update_fields.append("audiobook_duration")

        image_url = self._clean_value(data.get("image_url"))
        if image_url:
            self._replace_file_field(
                self.book,
                "image",
                image_url,
                fallback_name=f"mutolaa-{mutolaa_id or self.book.pk}-cover",
                log_label="book cover",
            )
            update_fields.append("image")

        ebook_file_url = self._clean_value(data.get("ebook_file_url"))
        if ebook_file_url:
            self._replace_file_field(
                self.book,
                "epub_file",
                ebook_file_url,
                fallback_name=f"mutolaa-{mutolaa_id or self.book.pk}",
                default_extension=".epub",
                log_label="ebook",
            )
            update_fields.append("epub_file")
        elif self.book.epub_file:
            self._log("Mutolaa has no ebook file; removing existing local ebook.")
            self.book.epub_file.delete(save=False)
            self.book.epub_file = None
            update_fields.append("epub_file")

        result.updated_fields.extend(update_fields)

    def _sync_authors(self, authors_data, result):
        authors = []
        self._log(f"Syncing {len(authors_data)} author(s).")
        for author_data in authors_data:
            mutolaa_id = self._clean_mutolaa_id(author_data.get("id"))
            if not mutolaa_id:
                continue

            author, created = Author.objects.get_or_create(
                mutolaa_id=mutolaa_id,
                defaults={"name": self._clean_value(author_data.get("name"))},
            )
            if created:
                result.created_authors += 1
            else:
                result.reused_authors += 1

            name = self._clean_value(author_data.get("name"))
            if name and author.name != name:
                author.name = name

            image_url = self._clean_value(author_data.get("image_url"))
            if image_url:
                self._replace_file_field(
                    author,
                    "image",
                    image_url,
                    fallback_name=f"mutolaa-author-{mutolaa_id}",
                    log_label=f"author image '{author.name}'",
                )
            elif author.image:
                self._log(
                    f"Mutolaa has no image for author '{author.name}'; removing local image."
                )
                author.image.delete(save=False)
                author.image = None

            author.save()
            authors.append(author)

        self.book.authors.set(authors)

    def _sync_genres(self, categories_data, result):
        genres = []
        self._log(f"Syncing {len(categories_data)} genre(s).")
        for _index, category_data in enumerate(categories_data):
            mutolaa_id = self._clean_mutolaa_id(category_data.get("id"))
            if not mutolaa_id:
                continue

            genre, created = Genre.objects.get_or_create(
                mutolaa_id=mutolaa_id,
                defaults={"title": self._clean_value(category_data.get("title"))},
            )
            if created:
                result.created_genres += 1
            else:
                result.reused_genres += 1

            title = self._clean_value(category_data.get("title"))
            if title and genre.title != title:
                genre.title = title
            genre.save()
            genres.append(genre)

        self.book.genres.set(genres)

    def _sync_audio_files(self, audiofiles_data, result):
        self._log(f"Syncing {len(audiofiles_data)} audio file(s).")
        self._delete_existing_audio_files()

        audio_files = []
        for index, audio_data in enumerate(audiofiles_data, start=1):
            file_url = self._clean_value(audio_data.get("file_url"))
            if not file_url:
                self._log(f"Skipping audio file #{index}: missing file_url.")
                continue

            order = audio_data.get("order") or 0
            title = self._clean_value(audio_data.get("title"))
            self._log(
                f"Preparing audio file #{index}/{len(audiofiles_data)} "
                f"(order={order}, title='{title}')."
            )
            audio_file = AudioFile(
                book=self.book,
                title=title,
                duration=audio_data.get("duration"),
                order=order,
            )
            self._replace_file_field(
                audio_file,
                "file",
                file_url,
                fallback_name=f"mutolaa-{self.book.mutolaa_id}-audio-{order}",
                default_extension=".mp3",
                log_label=f"audio file #{index}/{len(audiofiles_data)}",
            )
            audio_files.append(audio_file)

        for audio_file in audio_files:
            audio_file.save()
            self._log(
                f"Saved audio file order={audio_file.order}, "
                f"title='{audio_file.title}'."
            )

        result.created_audio_files = len(audio_files)

    def _delete_existing_audio_files(self):
        existing_audio_files = list(self.book.audio_files.all())
        if existing_audio_files:
            self._log(
                f"Deleting {len(existing_audio_files)} existing local audio file(s)."
            )

        for audio_file in existing_audio_files:
            if audio_file.file:
                audio_file.file.delete(save=False)
            audio_file.delete()

    def _replace_file_field(
        self,
        instance,
        field_name,
        url,
        *,
        fallback_name,
        default_extension="",
        log_label=None,
    ):
        log_label = log_label or field_name
        self._log(f"Downloading {log_label}: {url}")
        content = self._download_file(url)
        filename = self._filename_from_url(
            url,
            fallback_name=fallback_name,
            default_extension=default_extension,
        )
        self._log(f"Saving {log_label} as '{filename}' ({len(content)} bytes).")
        file_field = getattr(instance, field_name)
        if file_field:
            file_field.delete(save=False)
        file_field.save(filename, ContentFile(content), save=False)

    def _download_file(self, url):
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as exc:
            raise MutolaaBookSyncError(f"Could not download media file: {url}") from exc

    def _filename_from_url(self, url, *, fallback_name, default_extension=""):
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        if not filename:
            filename = fallback_name

        if "." not in filename:
            extension = default_extension or mimetypes.guess_extension(
                mimetypes.guess_type(url)[0] or ""
            )
            filename = f"{filename}{extension or ''}"

        return filename

    def _get_config(self):
        config = {
            "base_url": self._clean_value(self.config.get("base_url")),
            "username": self._clean_value(self.config.get("username")),
            "password": self._clean_value(self.config.get("password")),
        }
        missing_keys = [key for key, value in config.items() if not value]
        if missing_keys:
            raise MutolaaBookSyncError(
                "Missing Mutolaa config values: " + ", ".join(missing_keys)
            )
        return config

    def _get_mutolaa_id(self):
        mutolaa_id = self._clean_mutolaa_id(self.book.mutolaa_id)
        if not mutolaa_id:
            raise MutolaaBookSyncError("Book does not have mutolaa_id.")

        try:
            return int(mutolaa_id)
        except ValueError as exc:
            raise MutolaaBookSyncError(
                f"Book mutolaa_id must be integer: {mutolaa_id!r}."
            ) from exc

    def _clean_value(self, value):
        if value is None:
            return ""
        return str(value).strip()

    def _clean_mutolaa_id(self, value):
        if value in (None, ""):
            return None
        return self._clean_value(value)

    def _log(self, message):
        logger.info(message)
        if self.log_callback:
            self.log_callback(message)
