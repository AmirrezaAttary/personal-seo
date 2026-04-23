from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse


class IsNotAuthenticated(BasePermission):
    """
    اجازه دسترسی فقط به کاربران ناشناس (Not logged in)
    اگر کاربر لاگین باشد، دسترسی رد می شود.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # ساخت آدرس داینامیک
            redirect_path = reverse('dashboard:api-v1-dashboard:home')  # اسم URL مربوط به /dashboard/v1/
            redirect_url = request.build_absolute_uri(redirect_path)

            # تنظیم پیام JSON داینامیک
            self.message = {
                "detail": "شما قبلاً وارد شده‌اید.",
                "redirect_url": redirect_url
            }
            return False  # یعنی دسترسی ندارد
        return True  # اجازه دسترسی دارد
