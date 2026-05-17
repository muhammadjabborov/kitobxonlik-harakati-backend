from rest_framework import serializers

from apps.book.models import Book
from apps.book.serializers import CategorySerializer, LanguageSerializer, AuthorSerializer




class BookDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    categories = CategorySerializer(many=True)
    language = LanguageSerializer()
    audio_duration = serializers.IntegerField(source="audio_duration_total", read_only=True)
    audio_book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "description",
            "slug",
            "categories",
            "published_year",
            "authors",
            "audio_duration",
            "audio_book_count",
            "language",
            "page_count",
            "grades",
            "featured_date",
        )
