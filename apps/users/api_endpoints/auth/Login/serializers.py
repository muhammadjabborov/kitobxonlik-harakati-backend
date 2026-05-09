from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    code = serializers.CharField(write_only=True)
    session = serializers.CharField(write_only=True)

    def validate_phone_number(self, phone_number):
        if not User.objects.filter(phone_number=str(phone_number)).exists():
            raise serializers.ValidationError(
                _("No user found with this phone number."), code="not_found"
            )
        return phone_number
