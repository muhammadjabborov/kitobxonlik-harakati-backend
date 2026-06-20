import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

from django.db import transaction

from apps.book.models import Author, Book
from apps.competition.models import (
    CompetitionMonth,
    CompetitionMonthBook,
    CompetitionMonthGrade,
    CompetitionSeason,
)
from apps.users.choices import GradeChoices


class CompetitionBooksImportError(Exception):
    pass


class ImportCompetitionBooksService:
    REQUIRED_FIELDS = {
        "grade",
        "is_mandatory",
        "month_start",
        "original_source_title",
    }

    def __init__(self, path, process_books_without_mutolaa_id=False):
        self.path = Path(path)
        self.process_books_without_mutolaa_id = process_books_without_mutolaa_id

    @transaction.atomic
    def import_books(self):
        all_records = self._load_records()
        records, skipped_count = self._filter_records(all_records)
        self._validate_records(records)
        season = self._get_active_season()
        stats = self._import_records(season, records)
        stats["records_total"] = len(all_records)
        stats["records_skipped_without_mutolaa_id"] = skipped_count
        stats["records_processed_without_mutolaa_id"] = sum(
            1
            for record in records
            if isinstance(record, dict)
            and not self._clean_mutolaa_id(record.get("mutolaa_id"))
        )
        return stats

    def _load_records(self):
        if not self.path.exists():
            raise CompetitionBooksImportError(f"JSON file does not exist: {self.path}")

        try:
            with self.path.open(encoding="utf-8") as file:
                records = json.load(file)
        except json.JSONDecodeError as exc:
            raise CompetitionBooksImportError(
                f"Invalid JSON in {self.path}: {exc}"
            ) from exc

        if not isinstance(records, list):
            raise CompetitionBooksImportError(
                "JSON root must be a list of dictionaries."
            )

        return records

    def _filter_records(self, records):
        if self.process_books_without_mutolaa_id:
            return records, 0

        return self._filter_records_with_mutolaa_id(records)

    def _filter_records_with_mutolaa_id(self, records):
        filtered_records = []
        skipped_count = 0

        for record in records:
            if not isinstance(record, dict):
                filtered_records.append(record)
                continue

            if self._clean_mutolaa_id(record.get("mutolaa_id")):
                filtered_records.append(record)
            else:
                skipped_count += 1

        return filtered_records, skipped_count

    def _validate_records(self, records):
        valid_grades = {choice.value for choice in GradeChoices}

        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise CompetitionBooksImportError(f"Row {index}: expected dictionary.")

            missing_fields = self.REQUIRED_FIELDS - set(record)
            if missing_fields:
                fields = ", ".join(sorted(missing_fields))
                raise CompetitionBooksImportError(
                    f"Row {index}: missing required fields: {fields}."
                )

            mutolaa_id = self._clean_mutolaa_id(record.get("mutolaa_id"))

            title = self._clean_value(record["original_source_title"])
            if not title:
                raise CompetitionBooksImportError(
                    f"Row {index}: original_source_title is empty."
                )
            if len(title) > Book._meta.get_field("title").max_length:
                raise CompetitionBooksImportError(
                    f"Row {index}: title is longer than Book.title max_length."
                )

            if not mutolaa_id:
                if "authors" not in record:
                    raise CompetitionBooksImportError(
                        f"Row {index}: missing required fields: authors."
                    )

                authors = record["authors"]
                if not isinstance(authors, list) or not authors:
                    raise CompetitionBooksImportError(
                        f"Row {index}: authors must be a non-empty list."
                    )
                if any(not self._clean_value(author) for author in authors):
                    raise CompetitionBooksImportError(
                        f"Row {index}: authors contains an empty value."
                    )

            if record["grade"] not in valid_grades:
                raise CompetitionBooksImportError(
                    f"Row {index}: invalid grade: {record['grade']!r}."
                )

            try:
                date.fromisoformat(record["month_start"])
            except (TypeError, ValueError) as exc:
                raise CompetitionBooksImportError(
                    f"Row {index}: invalid month_start: {record['month_start']!r}."
                ) from exc

            if not isinstance(record["is_mandatory"], bool):
                raise CompetitionBooksImportError(
                    f"Row {index}: is_mandatory must be boolean."
                )

    def _get_active_season(self):
        try:
            return CompetitionSeason.objects.get(is_active=True)
        except CompetitionSeason.DoesNotExist as exc:
            raise CompetitionBooksImportError(
                "Active competition season was not found."
            ) from exc
        except CompetitionSeason.MultipleObjectsReturned as exc:
            raise CompetitionBooksImportError(
                "More than one active competition season exists."
            ) from exc

    def _import_records(self, season, records):
        stats = Counter(records=len(records))
        author_cache = self._build_author_cache()
        (
            book_cache_by_mutolaa_id,
            book_cache_by_title_authors,
            book_cache_by_title,
        ) = self._build_book_caches()

        for record in records:
            month, created = CompetitionMonth.objects.get_or_create(
                season=season,
                month_start=date.fromisoformat(record["month_start"]),
                defaults={"is_active": True},
            )
            stats[
                "competition_months_created" if created else "competition_months_reused"
            ] += 1

            month_grade, created = CompetitionMonthGrade.objects.get_or_create(
                month=month,
                grade=record["grade"],
            )
            stats[
                "competition_month_grades_created"
                if created
                else "competition_month_grades_reused"
            ] += 1

            mutolaa_id = self._clean_mutolaa_id(record.get("mutolaa_id"))
            authors = []
            if not mutolaa_id:
                authors = [
                    self._get_or_create_author(author_name, author_cache, stats)
                    for author_name in record["authors"]
                ]

            book = self._get_or_create_book(
                record=record,
                authors=authors,
                book_cache_by_mutolaa_id=book_cache_by_mutolaa_id,
                book_cache_by_title_authors=book_cache_by_title_authors,
                book_cache_by_title=book_cache_by_title,
                stats=stats,
            )

            month_book, created = CompetitionMonthBook.objects.get_or_create(
                month_grade=month_grade,
                book=book,
                defaults={"is_required": record["is_mandatory"]},
            )
            if created:
                stats["competition_month_books_created"] += 1
            elif month_book.is_required != record["is_mandatory"]:
                month_book.is_required = record["is_mandatory"]
                month_book.save(update_fields=["is_required", "updated_at"])
                stats["competition_month_books_updated"] += 1
            else:
                stats["competition_month_books_reused"] += 1

        return stats

    def _build_author_cache(self):
        return {
            self._normalize(author.name): author
            for author in Author.objects.all().order_by("id")
        }

    def _build_book_caches(self):
        by_mutolaa_id = {}
        by_title_authors = {}
        by_title = {}

        for book in Book.objects.prefetch_related("authors").order_by("id"):
            if book.mutolaa_id and book.mutolaa_id not in by_mutolaa_id:
                by_mutolaa_id[book.mutolaa_id] = book

            normalized_title = self._normalize(book.title)
            if normalized_title:
                author_key = self._author_key(book.authors.all())
                by_title_authors.setdefault((normalized_title, author_key), book)
                by_title.setdefault(normalized_title, []).append(book)

        return by_mutolaa_id, by_title_authors, by_title

    def _get_or_create_author(self, author_name, author_cache, stats):
        author_name = self._clean_value(author_name)
        normalized_name = self._normalize(author_name)

        author = author_cache.get(normalized_name)
        if author:
            stats["authors_reused"] += 1
            return author

        author = Author.objects.create(name=author_name)
        author_cache[normalized_name] = author
        stats["authors_created"] += 1
        return author

    def _get_or_create_book(
        self,
        *,
        record,
        authors,
        book_cache_by_mutolaa_id,
        book_cache_by_title_authors,
        book_cache_by_title,
        stats,
    ):
        title = self._clean_value(record["original_source_title"])
        fallback_title = self._clean_value(record.get("book_title"))
        mutolaa_id = self._clean_mutolaa_id(record.get("mutolaa_id"))
        author_key = self._author_key(authors)

        book = None
        if mutolaa_id:
            book = book_cache_by_mutolaa_id.get(mutolaa_id)
            if book is None:
                book = Book.objects.create(
                    title=title,
                    description="",
                    image="",
                    mutolaa_id=mutolaa_id,
                )
                stats["books_created"] += 1
            else:
                stats["books_reused"] += 1

            self._cache_book(
                book,
                book_cache_by_mutolaa_id,
                book_cache_by_title_authors,
                book_cache_by_title,
            )
            return book

        if book is None:
            for candidate in (title, fallback_title):
                normalized_title = self._normalize(candidate)
                if normalized_title:
                    book = book_cache_by_title_authors.get(
                        (normalized_title, author_key)
                    )
                    if book:
                        break

        if book is None:
            for candidate in (title, fallback_title):
                normalized_title = self._normalize(candidate)
                title_matches = book_cache_by_title.get(normalized_title, [])
                if len(title_matches) == 1 and not title_matches[0].authors.exists():
                    book = title_matches[0]
                    break

        if book is None:
            book = Book.objects.create(
                title=title,
                description="",
                image="",
                mutolaa_id=mutolaa_id,
            )
            stats["books_created"] += 1
        else:
            stats["books_reused"] += 1

        for author in authors:
            if not book.authors.filter(pk=author.pk).exists():
                book.authors.add(author)
                stats["book_authors_added"] += 1

        self._cache_book(
            book,
            book_cache_by_mutolaa_id,
            book_cache_by_title_authors,
            book_cache_by_title,
        )

        return book

    def _cache_book(
        self,
        book,
        book_cache_by_mutolaa_id,
        book_cache_by_title_authors,
        book_cache_by_title,
    ):
        if book.mutolaa_id:
            book_cache_by_mutolaa_id.setdefault(book.mutolaa_id, book)

        normalized_title = self._normalize(book.title)
        if normalized_title:
            author_key = self._author_key(book.authors.all())
            book_cache_by_title_authors.setdefault(
                (normalized_title, author_key),
                book,
            )
            title_matches = book_cache_by_title.setdefault(normalized_title, [])
            if book not in title_matches:
                title_matches.append(book)

    def _author_key(self, authors):
        return tuple(sorted(self._normalize(author.name) for author in authors))

    def _clean_value(self, value):
        if value is None:
            return ""
        return re.sub(r"\s+", " ", str(value)).strip()

    def _clean_mutolaa_id(self, value):
        if value in (None, ""):
            return None
        return self._clean_value(value)

    def _normalize(self, value):
        value = self._clean_value(value).lower()
        value = unicodedata.normalize("NFKC", value)
        value = value.translate(
            str.maketrans(
                {
                    # "ʻ": "'",
                    # "‘": "'",
                    # "’": "'",
                    # "`": "'",
                    # "ʼ": "'",
                    # "“": '"',
                    # "”": '"',
                    "«": '"',
                    "»": '"',
                }
            )
        )
        value = re.sub(r"[\"'().,:;!?-]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()
