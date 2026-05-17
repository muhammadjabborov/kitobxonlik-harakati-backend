from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.book.api_endpoints.book.AudioBookDetail.serializers import AudioFileDetailSerializer
from apps.book.models import AudioFile


class AudioBookDetailView(generics.RetrieveAPIView):
    serializer_class = AudioFileDetailSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return get_object_or_404(
            AudioFile.objects.select_related("book"),
            pk=self.kwargs["pk"],
        )


__all__ = ["AudioBookDetailView"]
