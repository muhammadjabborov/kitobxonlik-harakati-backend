from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.common.api_endpoints.common.SchoolList.serializers import SchoolSerializer
from apps.common.models import School


class SchoolListView(generics.ListAPIView):
    serializer_class = SchoolSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = School.objects.all()
        district_id = self.request.query_params.get("district_id")
        region_id = self.request.query_params.get("region_id")
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if region_id:
            queryset = queryset.filter(district__region_id=region_id)
        return queryset
