from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        # if not self.user.is_verified:
        #     raise serializers.ValidationError({"detail": "user is not verified"})
        validated_data["phone_number"] = self.user.phone_number
        validated_data["user_id"] = self.user.id
        return validated_data
