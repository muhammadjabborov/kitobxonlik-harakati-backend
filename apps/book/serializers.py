from rest_framework import serializers

from apps.book.models import Author, Book, Genre


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "title")


class BookShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "slug", "image")
