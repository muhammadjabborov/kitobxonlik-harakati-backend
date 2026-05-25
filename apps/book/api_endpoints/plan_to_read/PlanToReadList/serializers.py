from rest_framework import serializers

from apps.book.models import PlanToRead, Book
from apps.book.serializers import AuthorSerializer

class ShortBookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    class Meta:
        model = Book
        fields = ("id", "title", "slug", "image", "authors")


class PlanToReadListSerializer(serializers.ModelSerializer):
    book = ShortBookSerializer()

    class Meta:
        model = PlanToRead
        fields = ("id", "book")
