from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from django.contrib.auth import get_user_model

User = get_user_model()


class LogoutSerializer(serializers.Serializer):
    """Serializer ساده برای نمایش پیام خروج"""
    message = serializers.CharField(read_only=True)


class LogoutViewSet(viewsets.ModelViewSet):
    """
    خروج کاربر از حساب کاربری (POST)
    """
    serializer_class = LogoutSerializer
    queryset = User.objects.all()  # فقط برای ModelViewSet لازم است
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        """
        متد POST برای خروج از حساب کاربری
        """
        logout(request)
        return Response(
            {"message": "خروج با موفقیت انجام شد."},
            status=status.HTTP_200_OK
        )
