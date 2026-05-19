from rest_framework import serializers

from apps.common.models import Region
from apps.users.models import User


class RegionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name", "level")


class GetProfileSerializer(serializers.ModelSerializer):
    region = RegionShortSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone_number",
            "birth_date",
            "grade",
            "region",
            "identity_type",
            "identity_number",
        )
