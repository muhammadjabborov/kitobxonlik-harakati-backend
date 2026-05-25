from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from apps.book.models import PlanToRead


class PlanToReadDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PlanToRead.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(
            PlanToRead, user=self.request.user, book_id=self.kwargs["book_id"]
        )
