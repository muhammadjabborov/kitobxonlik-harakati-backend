from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.competition.services.import_competition_books import (
    CompetitionBooksImportError,
    ImportCompetitionBooksService,
)


class Command(BaseCommand):
    """
    example:
    python manage.py import_competition_books --path data/books_to_create.json --process-books-without-mutolaa-id
    """

    help = "Import competition books from data/books_to_create.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(settings.BASE_DIR / "data" / "books_to_create.json"),
            help="Path to the generated competition books JSON file.",
        )
        parser.add_argument(
            "--process-books-without-mutolaa-id",
            "--include-books-without-mutolaa-id",
            action="store_true",
            dest="process_books_without_mutolaa_id",
            help=(
                "Also import JSON records without mutolaa_id. Authors are only "
                "processed for those records."
            ),
        )

    def handle(self, *args, **options):
        service = ImportCompetitionBooksService(
            path=options["path"],
            process_books_without_mutolaa_id=options[
                "process_books_without_mutolaa_id"
            ],
        )

        try:
            stats = service.import_books()
        except CompetitionBooksImportError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("Competition books imported."))
        self._print_stats(stats)

    def _print_stats(self, stats):
        labels = [
            ("Records total", "records_total"),
            ("Records", "records"),
            (
                "Records skipped without mutolaa id",
                "records_skipped_without_mutolaa_id",
            ),
            (
                "Records processed without mutolaa id",
                "records_processed_without_mutolaa_id",
            ),
            ("Competition months created", "competition_months_created"),
            ("Competition months reused", "competition_months_reused"),
            ("Competition month grades created", "competition_month_grades_created"),
            ("Competition month grades reused", "competition_month_grades_reused"),
            ("Authors created", "authors_created"),
            ("Authors reused", "authors_reused"),
            ("Books created", "books_created"),
            ("Books reused", "books_reused"),
            ("Books updated", "books_updated"),
            ("Book-author links added", "book_authors_added"),
            ("Competition month books created", "competition_month_books_created"),
            ("Competition month books updated", "competition_month_books_updated"),
            ("Competition month books reused", "competition_month_books_reused"),
        ]

        for label, key in labels:
            self.stdout.write(f"{label}: {stats[key]}")
