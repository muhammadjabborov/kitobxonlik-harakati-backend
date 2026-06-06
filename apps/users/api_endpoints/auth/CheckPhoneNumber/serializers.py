from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers


class CheckPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_international_phonenumber])
