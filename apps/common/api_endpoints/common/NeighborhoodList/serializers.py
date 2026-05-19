from rest_framework import serializers

from apps.common.models import Region


class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name", "soato")
