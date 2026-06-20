from collections import Counter

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from apps.book.models import Book
from apps.book.services.mutolaa_book_sync import (
    MutolaaBookSyncError,
    MutolaaBookSyncService,
)


class Command(BaseCommand):
    """
    example:
    python manage.py sync_mutolaa_books
    """

    help = "Sync local books with Mutolaa data for books missing ebook or audio."

    def handle(self, *args, **options):
        stats = Counter()
        books = self._get_books_to_sync()
        total_books = books.count()

        self.stdout.write(f"Books to sync: {total_books}")

        for index, book in enumerate(books.iterator(), start=1):
            stats["processed"] += 1
            self.stdout.write(
                f"[{index}/{total_books}] [{book.pk}] {book.title}: starting sync"
            )
            try:
                result = MutolaaBookSyncService(
                    book,
                    log_callback=self._build_service_logger(book),
                ).sync()
            except MutolaaBookSyncError as exc:
                stats["failed"] += 1
                self.stderr.write(f"[{book.pk}] {book.title}: {exc}")
                continue

            stats["synced"] += 1
            stats["created_authors"] += result.created_authors
            stats["created_genres"] += result.created_genres
            stats["created_audio_files"] += result.created_audio_files
            self.stdout.write(f"[{book.pk}] {book.title}: synced")

        self._print_stats(stats)

    def _get_books_to_sync(self):
        return (
            Book.objects.annotate(audio_files_count=Count("audio_files"))
            .filter(mutolaa_id__isnull=False)
            .exclude(mutolaa_id="")
            .filter(
                Q(epub_file__isnull=True) | Q(epub_file="") | Q(audio_files_count=0)
            )
            .order_by("id")
        )

    def _build_service_logger(self, book):
        return lambda message: self._log_service_message(book, message)

    def _log_service_message(self, book, message):
        self.stdout.write(f"  [{book.pk}] {message}")

    def _print_stats(self, stats):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Mutolaa book sync finished."))
        self.stdout.write(f"Processed: {stats['processed']}")
        self.stdout.write(f"Synced: {stats['synced']}")
        self.stdout.write(f"Failed: {stats['failed']}")
        self.stdout.write(f"Created authors: {stats['created_authors']}")
        self.stdout.write(f"Created genres: {stats['created_genres']}")
        self.stdout.write(f"Created audio files: {stats['created_audio_files']}")
