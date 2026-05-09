from rest_framework import serializers

from apps.common.models import District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "name")
