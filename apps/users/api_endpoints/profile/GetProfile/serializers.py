from rest_framework import serializers

from apps.common.models import Region
from apps.users.models import User


class RegionSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ("id", "name", "soato", "level", "parent")
        ref_name = "ProfileRegionNested"

    def get_parent(self, obj):
        if obj.parent_id is None:
            return None
        return RegionSerializer(obj.parent).data


class GetProfileSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)

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
