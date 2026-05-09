from rest_framework import serializers

from apps.common.models import Region
from apps.users.models import User


class RegionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name")


class GetProfileSerializer(serializers.ModelSerializer):
    region = RegionShortSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone_number",
            "age",
            "grade",
            "school_number",
            "region",
            "identity_type",
            "identity_number",
        )
