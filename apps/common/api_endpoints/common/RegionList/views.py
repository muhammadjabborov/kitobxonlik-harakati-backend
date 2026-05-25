import django_filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.models import Region
from apps.common.api_endpoints.common.RegionList.serializers import RegionSerializer


class RegionFilter(django_filters.FilterSet):
    level = django_filters.NumberFilter(field_name="level")
    parent = django_filters.NumberFilter(field_name="parent_id")
    parent__isnull = django_filters.BooleanFilter(field_name="parent", lookup_expr="isnull")

    class Meta:
        model = Region
        fields = ["level", "parent", "parent__isnull"]


class RegionListView(ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = RegionFilter

    def get_queryset(self):
        return Region.objects.all().order_by("name")


__all__ = ["RegionListView"]
