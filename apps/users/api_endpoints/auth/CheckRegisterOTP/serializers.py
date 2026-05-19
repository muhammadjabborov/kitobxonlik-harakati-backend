from rest_framework import serializers


class CheckRegisterOTPSerializer(serializers.Serializer):
    session = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)
