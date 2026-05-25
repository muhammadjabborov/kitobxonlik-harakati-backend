from rest_framework import generics, permissions

from django.db import transaction

from .serializers import PlanToReadCreateSerializer

from apps.book.models import PlanToRead


class PlanToReadCreateAPIView(generics.CreateAPIView):
    serializer_class = PlanToReadCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return PlanToRead.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
