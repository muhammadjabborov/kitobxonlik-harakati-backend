from rest_framework import serializers

from apps.common.models import District, Neighborhood, Region
from apps.users.models import User


class RegionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name")


class DistrictShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "name")


class NeighborhoodShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = ("id", "name")


class GetProfileSerializer(serializers.ModelSerializer):
    region = RegionShortSerializer(read_only=True)
    district = DistrictShortSerializer(read_only=True)
    neighborhood = NeighborhoodShortSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone_number",
            "birth_date",
            "grade",
            "region",
            "district",
            "neighborhood",
            "identity_type",
            "identity_number",
        )
