from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from apps.common.models import Region
from apps.users.choices import GradeChoices, IdentityTypeChoices
from apps.users.models import User


class RegisterSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    full_name = serializers.CharField(max_length=256)
    age = serializers.IntegerField(min_value=1, max_value=100, required=False, allow_null=True)
    grade = serializers.ChoiceField(choices=GradeChoices.choices, required=False, allow_null=True)
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), required=False, allow_null=True
    )
    school_number = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    identity_type = serializers.ChoiceField(
        choices=IdentityTypeChoices.choices, required=False, allow_null=True
    )
    identity_number = serializers.CharField(max_length=64, required=False, allow_null=True)
    code = serializers.CharField(write_only=True)
    session = serializers.CharField(write_only=True)

    def validate_phone_number(self, phone_number):
        if User.objects.filter(phone_number=str(phone_number)).exists():
            raise serializers.ValidationError(
                _("A user with this phone number already exists."), code="already_exists"
            )
        return phone_number

    def validate(self, attrs):
        identity_number = attrs.get("identity_number")
        if identity_number and User.objects.filter(identity_number=identity_number).exists():
            raise serializers.ValidationError(
                {"identity_number": _("A user with this identity number already exists.")},
                code="already_exists",
            )
        return attrs
