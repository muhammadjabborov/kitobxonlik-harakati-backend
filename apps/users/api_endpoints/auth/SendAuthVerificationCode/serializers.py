from adrf.serializers import Serializer
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers


class SendVerificationCodeSerializer(Serializer):
    phone_number = serializers.CharField(validators=[validate_international_phonenumber])
