from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers import ChangePasswordSerializer

User = get_user_model()


class ChangePasswordApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check old password
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": ["رمز فعلی اشتباه است"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # set new password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )