from collections import Counter
from urllib.parse import urljoin

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.book.models import Book


class MutolaaBookMetadataSyncError(Exception):
    pass


class Command(BaseCommand):
    endpoint_path = "/api/v1/common/kitobxonlik-harakati/BookList/"
    help = "Update book descriptions and Mutolaa slugs from Mutolaa."

    def handle(self, *args, **options):
        stats = Counter()
        books = self._get_books_to_sync()
        total_books = books.count()

        self.stdout.write(f"Books to update: {total_books}")

        for index, book in enumerate(books.iterator(), start=1):
            stats["processed"] += 1
            self.stdout.write(
                f"[{index}/{total_books}] [{book.pk}] {book.title}: updating metadata"
            )
            try:
                updated_fields = self._sync_book_metadata(book)
            except MutolaaBookMetadataSyncError as exc:
                stats["failed"] += 1
                self.stderr.write(f"[{book.pk}] {book.title}: {exc}")
                continue

            if updated_fields:
                stats["updated"] += 1
                fields = ", ".join(updated_fields)
                self.stdout.write(f"[{book.pk}] {book.title}: updated {fields}")
            else:
                stats["unchanged"] += 1
                self.stdout.write(f"[{book.pk}] {book.title}: unchanged")

        self._print_stats(stats)

    def _get_books_to_sync(self):
        return (
            Book.objects.filter(mutolaa_id__isnull=False)
            .exclude(mutolaa_id="")
            .order_by("id")
        )

    def _sync_book_metadata(self, book):
        data = self._fetch_book_data(book)

        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=book.pk)
            updated_fields = []

            description = self._clean_value(data.get("description"))
            if description and book.description != description:
                book.description = description
                updated_fields.append("description")

            mutolaa_slug = self._clean_value(data.get("slug"))
            if mutolaa_slug and book.mutolaa_slug != mutolaa_slug:
                book.mutolaa_slug = mutolaa_slug
                updated_fields.append("mutolaa_slug")

            if updated_fields:
                book.save(update_fields=updated_fields)

        return updated_fields

    def _fetch_book_data(self, book):
        mutolaa_id = self._get_mutolaa_id(book)
        response_data = self._post_book_list([mutolaa_id])

        if not isinstance(response_data, list):
            raise MutolaaBookMetadataSyncError("Mutolaa response must be a list.")

        for item in response_data:
            if str(item.get("id")) == str(mutolaa_id):
                return item

        raise MutolaaBookMetadataSyncError(
            f"Mutolaa book was not found for id={mutolaa_id}."
        )

    def _post_book_list(self, book_ids):
        config = self._get_config()
        url = urljoin(
            config["base_url"].rstrip("/") + "/",
            self.endpoint_path.lstrip("/"),
        )

        try:
            with httpx.Client(
                timeout=config["timeout"], follow_redirects=True
            ) as client:
                response = client.post(
                    url,
                    json={"book_ids": book_ids},
                    auth=(config["username"], config["password"]),
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise MutolaaBookMetadataSyncError(
                f"Mutolaa API returned {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise MutolaaBookMetadataSyncError(
                "Could not connect to Mutolaa API."
            ) from exc
        except ValueError as exc:
            raise MutolaaBookMetadataSyncError(
                "Mutolaa API returned invalid JSON."
            ) from exc

    def _get_config(self):
        configured = settings.KITOBXONLIK_HARAKATI_CONFIG
        config = {
            "base_url": self._clean_value(configured.get("base_url")),
            "username": self._clean_value(configured.get("username")),
            "password": self._clean_value(configured.get("password")),
            "timeout": configured.get("timeout", 30),
        }
        missing_keys = [
            key for key in ("base_url", "username", "password") if not config[key]
        ]
        if missing_keys:
            raise MutolaaBookMetadataSyncError(
                "Missing Mutolaa config values: " + ", ".join(missing_keys)
            )
        return config

    def _get_mutolaa_id(self, book):
        mutolaa_id = self._clean_value(book.mutolaa_id)
        if not mutolaa_id:
            raise MutolaaBookMetadataSyncError("Book does not have mutolaa_id.")

        try:
            return int(mutolaa_id)
        except ValueError as exc:
            raise MutolaaBookMetadataSyncError(
                f"Book mutolaa_id must be integer: {mutolaa_id!r}."
            ) from exc

    @staticmethod
    def _clean_value(value):
        if value is None:
            return ""
        return str(value).strip()

    def _print_stats(self, stats):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Mutolaa book metadata sync finished."))
        self.stdout.write(f"Processed: {stats['processed']}")
        self.stdout.write(f"Updated: {stats['updated']}")
        self.stdout.write(f"Unchanged: {stats['unchanged']}")
        self.stdout.write(f"Failed: {stats['failed']}")
