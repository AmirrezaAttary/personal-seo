from rest_framework import viewsets, status,generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from ..serializers import RegistrationSerializer
from ..permissions import IsNotAuthenticated
from django.urls import reverse
from django.contrib.auth import get_user_model, login

User = get_user_model()


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsNotAuthenticated]  # 👈 اصلاح شد

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            phone_number = serializer.validated_data["phone_number"]
            data = {"phone_number": phone_number}
            user_obj = get_object_or_404(User, phone_number=phone_number)
            token = self.get_tokens_for_user(user_obj)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)