# pages/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class City(models.Model):
    """اختیاری: اگر می‌خوای شهرها قابل انتخاب از دیتابیس باشن."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"

    def __str__(self):
        return self.name


class Business(models.Model):
    CATEGORY_CHOICES = (
        ("shop", "مغازه"),
        ("company", "شرکت"),
        ("person", "شخص"),
        ("service", "خدمات"),
    )

    name = models.CharField(max_length=180, verbose_name="نام کسب‌وکار/شخص")
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="shop")

    # حوزه فعالیت (کلید اصلی سئو)
    activity = models.CharField(max_length=180, verbose_name="حوزه فعالیت")

    # شهر
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="businesses", null=True, blank=True)
    city_name = models.CharField(max_length=120, blank=True, default="", verbose_name="نام شهر (اگر City نداری)")

    short_description = models.TextField(max_length=500, blank=True, default="")
    about_text = models.TextField(blank=True, default="", verbose_name="متن معرفی/درباره ما")

    # تماس
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="تلفن")
    whatsapp = models.CharField(max_length=30, blank=True, default="", verbose_name="واتساپ (شماره)")
    email = models.EmailField(blank=True, default="")

    # آدرس (مدیریت جداگانه)
    # OneToOne برای اینکه هر کسب‌وکار یک آدرس داشته باشه (اختیاری)
    # در BusinessAddress مدل جدا نوشته شده

    # وضعیت انتشار
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "کسب‌وکار/صفحه معرفی"
        verbose_name_plural = "کسب‌وکارها"

    def __str__(self):
        return self.name

    def get_city_display(self):
        return self.city.name if self.city else self.city_name

    def save(self, *args, **kwargs):
        if not self.slug:
            city_part = self.get_city_display()
            base = f"{self.name}-{self.activity}-{city_part}".strip()
            self.slug = slugify(base)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # اگر مسیر detail را تنظیم کردی
        return reverse("business_detail", kwargs={"slug": self.slug})


class BusinessAddress(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="address")

    state = models.CharField(max_length=120, blank=True, default="", verbose_name="استان")
    address_line1 = models.CharField(max_length=220, blank=True, default="", verbose_name="آدرس ۱ (خیابان/پلاک)")
    address_line2 = models.CharField(max_length=220, blank=True, default="", verbose_name="آدرس ۲ (پلاک/طبقه/…)")
    postal_code = models.CharField(max_length=20, blank=True, default="", verbose_name="کدپستی")

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    google_map_url = models.URLField(blank=True, default="", verbose_name="لینک گوگل مپ")

    class Meta:
        verbose_name = "آدرس کسب‌وکار"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"Address: {self.business.name}"


class BusinessSeo(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="seo")

    title = models.CharField(max_length=160, blank=True, default="", verbose_name="SEO Title")
    description = models.CharField(max_length=320, blank=True, default="", verbose_name="SEO Description")
    keywords = models.CharField(max_length=250, blank=True, default="", verbose_name="SEO Keywords")

    og_image = models.URLField(blank=True, default="", verbose_name="OG Image URL")
    robots_index = models.BooleanField(default=True)

    # (اختیاری) structured data / JSON-LD template می‌تونی بعداً اضافه کنی

    class Meta:
        verbose_name = "تنظیمات سئو"
        verbose_name_plural = "تنظیمات سئو"

    def __str__(self):
        return f"SEO: {self.business.name}"
