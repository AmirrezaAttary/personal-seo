from rest_framework import serializers
from ....models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "birth_date",
            "image",
        ]
        read_only_fields = ["phone_number"]