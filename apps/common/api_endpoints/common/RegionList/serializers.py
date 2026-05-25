from rest_framework import serializers

from apps.common.models import Region


class RegionSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ("id", "name", "soato", "level", "parent")
        ref_name = "RegionNested"

    def get_parent(self, obj):
        if obj.parent_id is None:
            return None
        return RegionSerializer(obj.parent).data
