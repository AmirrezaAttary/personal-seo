# pages/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.files.base import ContentFile


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"

    def __str__(self):
        return self.name


class Business(models.Model):
    CATEGORY_CHOICES = (
        ("shop",    "مغازه"),
        ("company", "شرکت"),
        ("person",  "شخص / فریلنسر"),
        ("service", "خدمات"),
    )

    name     = models.CharField(max_length=180, verbose_name="نام کسب‌وکار/شخص")
    slug     = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="shop")

    logo = models.ImageField(
        upload_to="businesses/logos/",
        blank=True, null=True,
        verbose_name="لوگو / تصویر",
    )

    activity          = models.CharField(max_length=180, verbose_name="حوزه فعالیت")
    city              = models.ForeignKey(City, on_delete=models.PROTECT, related_name="businesses", null=True, blank=True)
    city_name         = models.CharField(max_length=120, blank=True, default="", verbose_name="نام شهر (اگر City نداری)")
    short_description = models.TextField(max_length=500, blank=True, default="")
    about_text        = models.TextField(blank=True, default="", verbose_name="متن معرفی/درباره ما")

    phone     = models.CharField(max_length=30, blank=True, default="", verbose_name="تلفن")
    whatsapp  = models.CharField(max_length=30, blank=True, default="", verbose_name="واتساپ")
    email     = models.EmailField(blank=True, default="")
    website   = models.URLField(blank=True, default="", verbose_name="وب‌سایت")

    is_verified = models.BooleanField(default=False, verbose_name="تایید شده")
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    # QR Code — ذخیره به صورت SVG
    qr_code = models.ImageField(
        upload_to="businesses/qrcodes/",
        blank=True, null=True,
        verbose_name="QR Code",
    )

    class Meta:
        verbose_name        = "کسب‌وکار"
        verbose_name_plural = "کسب‌وکارها"
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["activity"]),
        ]

    def __str__(self):
        return self.name

    def get_city_display_name(self):
        return self.city.name if self.city else self.city_name

    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"slug": self.slug})

    def generate_qr_code(self, base_url="https://jostajo.ir"):
        """تولید QR Code برای صفحه این کسب‌وکار"""
        url = f"{base_url}{self.get_absolute_url()}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0B6FBF", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_{self.slug}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            city_part = self.get_city_display_name()
            base = f"{self.name}-{self.activity}-{city_part}".strip()
            self.slug = slugify(base)[:220]

        # اگه QR نداشت، بساز
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new or not self.qr_code:
            self.generate_qr_code()
            # فقط فیلد qr_code رو آپدیت کن
            Business.objects.filter(pk=self.pk).update(qr_code=self.qr_code)


class BusinessAddress(models.Model):
    business      = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="address")
    state         = models.CharField(max_length=120, blank=True, default="", verbose_name="استان")
    address_line1 = models.CharField(max_length=220, blank=True, default="", verbose_name="آدرس")
    address_line2 = models.CharField(max_length=220, blank=True, default="", verbose_name="آدرس ۲")
    postal_code   = models.CharField(max_length=20,  blank=True, default="", verbose_name="کدپستی")
    latitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_map_url = models.URLField(blank=True, default="", verbose_name="لینک گوگل مپ")

    class Meta:
        verbose_name        = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"Address: {self.business.name}"


class BusinessSocialLinks(models.Model):
    """شبکه‌های اجتماعی کسب‌وکار"""
    business  = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="social")

    instagram = models.CharField(max_length=100, blank=True, default="", verbose_name="اینستاگرام (یوزرنیم)")
    telegram  = models.CharField(max_length=100, blank=True, default="", verbose_name="تلگرام (یوزرنیم یا لینک)")
    linkedin  = models.URLField(blank=True, default="", verbose_name="لینکدین (URL)")
    twitter   = models.CharField(max_length=100, blank=True, default="", verbose_name="توییتر/X (یوزرنیم)")
    youtube   = models.URLField(blank=True, default="", verbose_name="یوتیوب (URL)")
    aparat    = models.CharField(max_length=100, blank=True, default="", verbose_name="آپارات (یوزرنیم)")
    rubika    = models.URLField(blank=True, default="", verbose_name="روبیکا (URL)")

    class Meta:
        verbose_name        = "شبکه‌های اجتماعی"
        verbose_name_plural = "شبکه‌های اجتماعی"

    def __str__(self):
        return f"Social: {self.business.name}"

    def get_instagram_url(self):
        if self.instagram:
            u = self.instagram.lstrip("@")
            return f"https://instagram.com/{u}"
        return ""

    def get_telegram_url(self):
        if self.telegram:
            if self.telegram.startswith("http"):
                return self.telegram
            u = self.telegram.lstrip("@")
            return f"https://t.me/{u}"
        return ""

    def get_twitter_url(self):
        if self.twitter:
            u = self.twitter.lstrip("@")
            return f"https://x.com/{u}"
        return ""

    def get_aparat_url(self):
        if self.aparat:
            return f"https://aparat.com/{self.aparat}"
        return ""

    def has_any(self):
        return any([
            self.instagram, self.telegram, self.linkedin,
            self.twitter, self.youtube, self.aparat, self.rubika
        ])


class BusinessSeo(models.Model):
    business      = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="seo")
    title         = models.CharField(max_length=160, blank=True, default="", verbose_name="SEO Title")
    description   = models.CharField(max_length=320, blank=True, default="", verbose_name="SEO Description")
    keywords      = models.CharField(max_length=250, blank=True, default="", verbose_name="Keywords")
    og_image      = models.URLField(blank=True, default="", verbose_name="OG Image URL")
    robots_index  = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "تنظیمات سئو"
        verbose_name_plural = "تنظیمات سئو"

    def __str__(self):
        return f"SEO: {self.business.name}"