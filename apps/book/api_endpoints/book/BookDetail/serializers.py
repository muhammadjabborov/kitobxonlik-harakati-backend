from rest_framework import serializers

from apps.book.models import Book
from apps.book.serializers import AuthorSerializer, GenreSerializer


class BookDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)
    audio_duration = serializers.IntegerField(
        source="audio_duration_total", read_only=True
    )
    audio_book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "description",
            "image",
            "slug",
            "genres",
            "authors",
            "audio_duration",
            "audio_book_count",
            "epub_file",
        )
