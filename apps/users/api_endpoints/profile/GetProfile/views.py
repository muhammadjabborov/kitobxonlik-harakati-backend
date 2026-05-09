from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from apps.users.api_endpoints.profile.GetProfile.serializers import GetProfileSerializer


class GetProfileView(RetrieveAPIView):
    serializer_class = GetProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return (
            self.request.user.__class__.objects
            .select_related("region")
            .get(pk=self.request.user.pk)
        )


__all__ = ["GetProfileView"]
