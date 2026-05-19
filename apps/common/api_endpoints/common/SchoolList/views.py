from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.common.api_endpoints.common.SchoolList.serializers import SchoolSerializer
from apps.common.models import School


class SchoolListView(generics.ListAPIView):
    serializer_class = SchoolSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "district_id",
                openapi.IN_QUERY,
                description="Filter schools by district ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "region_id",
                openapi.IN_QUERY,
                description="Filter schools by region ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = School.objects.all()
        district_id = self.request.query_params.get("district_id")
        region_id = self.request.query_params.get("region_id")
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if region_id:
            queryset = queryset.filter(district__parent_id=region_id)
        return queryset


__all__ = ["SchoolListView"]
