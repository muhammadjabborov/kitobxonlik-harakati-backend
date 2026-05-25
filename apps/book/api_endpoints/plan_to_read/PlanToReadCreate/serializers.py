from rest_framework import serializers

from apps.book.models import PlanToRead


class PlanToReadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanToRead
        fields = ("id", "book")

    def create(self, validated_data):
        instance, _ = PlanToRead.objects.get_or_create(**validated_data)
        return instance
