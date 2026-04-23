from django.db import models
from django.utils import timezone


class OTP(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).seconds < 300  # معتبر تا ۵ دقیقه
    
    @classmethod
    def create_otp(cls, user):
        import random
        code = f"{random.randint(10000, 99999)}"
        otp = cls.objects.create(user=user, code=code)
        return otp