from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):

        if attrs["new_password"] != attrs["new_password1"]:
            raise serializers.ValidationError("Password mismatch")

        try:
            validate_password(attrs["new_password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return super().validate(attrs)