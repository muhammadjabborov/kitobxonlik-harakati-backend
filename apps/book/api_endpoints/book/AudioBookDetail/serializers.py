from rest_framework import serializers

from apps.book.models import AudioFile
from apps.book.serializers import BookShortSerializer


class AudioFileDetailSerializer(serializers.ModelSerializer):
    book_info = BookShortSerializer(source="book")

    class Meta:
        model = AudioFile
        fields = ("id", "book_info", "title", "file", "duration", "order")
