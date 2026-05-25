import django_filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from apps.common.models import Region
from apps.common.api_endpoints.common.RegionList.serializers import RegionSerializer


class RegionFilter(django_filters.FilterSet):
    parent = django_filters.NumberFilter(field_name="parent_id", lookup_expr="exact")
    is_region = django_filters.BooleanFilter(method="filter_is_region")

    class Meta:
        model = Region
        fields = ["parent", "is_region"]

    def filter_is_region(self, queryset, name, value):
        if value:
            return queryset.filter(parent__isnull=True)
        return queryset


class RegionListView(ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RegionFilter
    search_fields = ["name"]

    def get_queryset(self):
        parent = self.request.query_params.get("parent")
        is_region = self.request.query_params.get("is_region")

        if not parent and not is_region:
            raise ValidationError(
                {"detail": "You must provide either 'parent' or 'is_region' query parameter."}
            )

        return Region.objects.select_related("parent__parent").order_by("name")


__all__ = ["RegionListView"]
