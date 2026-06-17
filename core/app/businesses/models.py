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
    


# ─────────────────────────────────────────────────────────────────
#  اضافه کردن به pages/models.py
#  ۱. BusinessTheme   — تم کارت ویزیت لوکس
#  ۲. BusinessDocument — فایل‌های قابل دانلود
#  ۳. BusinessEndorsement — تاییدیه‌ها
#  ۴. BusinessSocialLinks (نسخه جدید با بله + فیلدهای بیشتر)
# ─────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════
# ۱. BusinessTheme
# ══════════════════════════════════════════════════════════════════
class BusinessTheme(models.Model):
    """
    تنظیمات ظاهری کارت ویزیت.
    وقتی is_premium=True باشه، تمپلیت لوکس (طلایی/مشکی) لود میشه.
    """

    THEME_CHOICES = (
        ("default",      "پیش‌فرض سایت"),
        ("gold_black",   "طلایی / مشکی"),
        ("silver_dark",  "نقره‌ای / تیره"),
        ("rose_gold",    "رز گلد"),
        ("midnight_blue","آبی تیره شب"),
    )

    FONT_CHOICES = (
        ("vazirmatn", "وزیرمتن"),
        ("yekan",     "یکان"),
        ("sahel",     "ساحل"),
        ("dana",      "دانا"),
    )

    business   = models.OneToOneField(
        "Business", on_delete=models.CASCADE, related_name="theme"
    )
    is_premium = models.BooleanField(
        default=False, verbose_name="کارت ویزیت لوکس (Premium)"
    )
    theme      = models.CharField(
        max_length=30, choices=THEME_CHOICES, default="default",
        verbose_name="تم رنگی"
    )
    font       = models.CharField(
        max_length=30, choices=FONT_CHOICES, default="vazirmatn",
        verbose_name="فونت"
    )

    # رنگ‌های سفارشی (اختیاری — اگه خالی بمونه از تم پیش‌فرض استفاده میشه)
    primary_color     = models.CharField(
        max_length=20, blank=True, default="",
        verbose_name="رنگ اصلی (hex)", help_text="مثال: #C9A84C"
    )
    secondary_color   = models.CharField(
        max_length=20, blank=True, default="",
        verbose_name="رنگ ثانویه (hex)"
    )
    background_color  = models.CharField(
        max_length=20, blank=True, default="",
        verbose_name="رنگ پس‌زمینه (hex)"
    )
    text_color        = models.CharField(
        max_length=20, blank=True, default="",
        verbose_name="رنگ متن (hex)"
    )

    # تصویر پس‌زمینه هدر (اختیاری)
    header_bg_image   = models.ImageField(
        upload_to="businesses/themes/",
        blank=True, null=True,
        verbose_name="تصویر پس‌زمینه هدر"
    )

    # متن پایین کارت
    tagline = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="شعار / تگ‌لاین"
    )

    class Meta:
        verbose_name        = "تم کارت ویزیت"
        verbose_name_plural = "تم‌های کارت ویزیت"

    def __str__(self):
        return f"Theme: {self.business.name} ({'Premium' if self.is_premium else 'Default'})"

    # رنگ‌های آماده بر اساس تم انتخاب‌شده
    THEME_PRESETS = {
        "gold_black": {
            "primary":    "#C9A84C",
            "secondary":  "#B8963E",
            "background": "#0D0D0D",
            "text":       "#F5E6C8",
            "accent":     "#FFD700",
        },
        "silver_dark": {
            "primary":    "#A8A9AD",
            "secondary":  "#C0C0C0",
            "background": "#1A1A2E",
            "text":       "#E8E8E8",
            "accent":     "#C0C0C0",
        },
        "rose_gold": {
            "primary":    "#B76E79",
            "secondary":  "#C9818A",
            "background": "#1C1012",
            "text":       "#F8E8EA",
            "accent":     "#E8B4B8",
        },
        "midnight_blue": {
            "primary":    "#4A90D9",
            "secondary":  "#2C5F8A",
            "background": "#0A0F1E",
            "text":       "#D0E4F7",
            "accent":     "#6BB3E8",
        },
        "default": {
            "primary":    "#0B6FBF",
            "secondary":  "#0957a0",
            "background": "#eef2f7",
            "text":       "#111111",
            "accent":     "#0B6FBF",
        },
    }

    def get_colors(self):
        """برگردوندن رنگ‌های نهایی (سفارشی یا پیش‌فرض تم)"""
        preset = self.THEME_PRESETS.get(self.theme, self.THEME_PRESETS["default"])
        return {
            "primary":    self.primary_color    or preset["primary"],
            "secondary":  self.secondary_color  or preset["secondary"],
            "background": self.background_color or preset["background"],
            "text":       self.text_color       or preset["text"],
            "accent":     preset["accent"],
        }


# ══════════════════════════════════════════════════════════════════
# ۲. BusinessDocument
# ══════════════════════════════════════════════════════════════════
def business_document_upload_path(instance, filename):
    return f"businesses/documents/{instance.business.slug}/{filename}"


class BusinessDocument(models.Model):
    """فایل‌های قابل دانلود برای هر کسب‌وکار (مجوز، کاتالوگ، رزومه و ...)"""

    DOC_TYPE_CHOICES = (
        ("license",   "مجوز / پروانه فعالیت"),
        ("catalog",   "کاتالوگ / بروشور"),
        ("resume",    "رزومه"),
        ("portfolio", "نمونه کار"),
        ("price_list","لیست قیمت"),
        ("cert",      "گواهینامه / افتخارنامه"),
        ("other",     "سایر"),
    )

    business     = models.ForeignKey(
        "Business", on_delete=models.CASCADE, related_name="documents"
    )
    title        = models.CharField(max_length=120, verbose_name="عنوان فایل")
    doc_type     = models.CharField(
        max_length=20, choices=DOC_TYPE_CHOICES, default="other",
        verbose_name="نوع سند"
    )
    file         = models.FileField(
        upload_to=business_document_upload_path,
        verbose_name="فایل"
    )
    description  = models.CharField(
        max_length=220, blank=True, default="",
        verbose_name="توضیح کوتاه"
    )
    is_public    = models.BooleanField(
        default=True,
        verbose_name="نمایش عمومی",
        help_text="اگه غیرفعال باشه فقط در پنل ادمین قابل مشاهده‌ست"
    )
    order        = models.PositiveSmallIntegerField(
        default=0, verbose_name="ترتیب نمایش"
    )
    uploaded_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "فایل / سند"
        verbose_name_plural = "فایل‌ها / اسناد"
        ordering            = ["order", "-uploaded_at"]

    def __str__(self):
        return f"{self.title} — {self.business.name}"

    def get_file_extension(self):
        import os
        _, ext = os.path.splitext(self.file.name)
        return ext.lower().lstrip(".")

    def get_icon(self):
        ext = self.get_file_extension()
        icons = {
            "pdf":  "ti-file-type-pdf",
            "doc":  "ti-file-type-doc",
            "docx": "ti-file-type-doc",
            "xls":  "ti-file-spreadsheet",
            "xlsx": "ti-file-spreadsheet",
            "ppt":  "ti-presentation",
            "pptx": "ti-presentation",
            "zip":  "ti-file-zip",
            "rar":  "ti-file-zip",
            "jpg":  "ti-photo",
            "jpeg": "ti-photo",
            "png":  "ti-photo",
        }
        return icons.get(ext, "ti-file")


# ══════════════════════════════════════════════════════════════════
# ۳. BusinessEndorsement
# ══════════════════════════════════════════════════════════════════
class BusinessEndorsement(models.Model):
    """تاییدیه‌ها — مثل تاییدیه رئیس اتاق اصناف"""

    business       = models.ForeignKey(
        "Business", on_delete=models.CASCADE, related_name="endorsements"
    )
    issuer_name    = models.CharField(
        max_length=120, verbose_name="نام صادرکننده",
        help_text="مثال: رئیس اتاق اصناف تهران"
    )
    issuer_title   = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="سمت صادرکننده"
    )
    issuer_photo   = models.ImageField(
        upload_to="businesses/endorsements/",
        blank=True, null=True,
        verbose_name="عکس صادرکننده"
    )
    endorsement_text = models.TextField(
        verbose_name="متن تاییدیه",
        help_text="متن دقیق تاییدیه که روی کارت نمایش داده میشه"
    )
    badge_label    = models.CharField(
        max_length=60, blank=True, default="",
        verbose_name="برچسب badge",
        help_text="مثال: «تایید شده توسط اتاق اصناف» — اگه خالی باشه نام صادرکننده نشون داده میشه"
    )
    issued_date    = models.DateField(
        blank=True, null=True, verbose_name="تاریخ صدور"
    )
    expiry_date    = models.DateField(
        blank=True, null=True, verbose_name="تاریخ انقضا"
    )
    is_active      = models.BooleanField(default=True, verbose_name="نمایش")
    order          = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name        = "تاییدیه"
        verbose_name_plural = "تاییدیه‌ها"
        ordering            = ["order", "-issued_date"]

    def __str__(self):
        return f"{self.issuer_name} ← {self.business.name}"

    def get_badge_text(self):
        return self.badge_label or self.issuer_name

    @property
    def is_expired(self):
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


# ══════════════════════════════════════════════════════════════════
# ۴. BusinessSocialLinks — نسخه جدید (جایگزین مدل قبلی)
# ══════════════════════════════════════════════════════════════════
class BusinessSocialLinks(models.Model):
    """شبکه‌های اجتماعی — نسخه گسترش‌یافته"""

    business  = models.OneToOneField(
        "Business", on_delete=models.CASCADE, related_name="social"
    )

    # ─── ایرانی ───
    telegram  = models.CharField(max_length=120, blank=True, default="", verbose_name="تلگرام (یوزرنیم یا لینک)")
    instagram = models.CharField(max_length=100, blank=True, default="", verbose_name="اینستاگرام (یوزرنیم)")
    aparat    = models.CharField(max_length=100, blank=True, default="", verbose_name="آپارات (یوزرنیم)")
    rubika    = models.URLField(blank=True, default="", verbose_name="روبیکا (URL)")
    bale      = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="بله (یوزرنیم یا لینک)",
        help_text="یوزرنیم یا لینک کامل t.me مثل @username"
    )
    eitaa     = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="ایتا (یوزرنیم یا لینک)"
    )
    gap       = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="گپ (یوزرنیم)"
    )
    soroush   = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="سروش (یوزرنیم)"
    )

    # ─── بین‌المللی ───
    linkedin  = models.URLField(blank=True, default="", verbose_name="لینکدین (URL)")
    twitter   = models.CharField(max_length=100, blank=True, default="", verbose_name="توییتر/X (یوزرنیم)")
    youtube   = models.URLField(blank=True, default="", verbose_name="یوتیوب (URL)")
    tiktok    = models.CharField(max_length=100, blank=True, default="", verbose_name="تیک‌تاک (یوزرنیم)")
    pinterest = models.CharField(max_length=100, blank=True, default="", verbose_name="پینترست (یوزرنیم)")
    facebook  = models.CharField(max_length=100, blank=True, default="", verbose_name="فیسبوک (یوزرنیم یا URL)")
    snapchat  = models.CharField(max_length=100, blank=True, default="", verbose_name="اسنپ‌چت (یوزرنیم)")

    class Meta:
        verbose_name        = "شبکه‌های اجتماعی"
        verbose_name_plural = "شبکه‌های اجتماعی"

    def __str__(self):
        return f"Social: {self.business.name}"

    # ─── URL builders ───
    def get_instagram_url(self):
        if self.instagram:
            return f"https://instagram.com/{self.instagram.lstrip('@')}"
        return ""

    def get_telegram_url(self):
        if self.telegram:
            if self.telegram.startswith("http"):
                return self.telegram
            return f"https://t.me/{self.telegram.lstrip('@')}"
        return ""

    def get_twitter_url(self):
        if self.twitter:
            return f"https://x.com/{self.twitter.lstrip('@')}"
        return ""

    def get_aparat_url(self):
        if self.aparat:
            return f"https://aparat.com/{self.aparat}"
        return ""

    def get_tiktok_url(self):
        if self.tiktok:
            return f"https://tiktok.com/@{self.tiktok.lstrip('@')}"
        return ""

    def get_pinterest_url(self):
        if self.pinterest:
            return f"https://pinterest.com/{self.pinterest.lstrip('@')}"
        return ""

    def get_facebook_url(self):
        if self.facebook:
            if self.facebook.startswith("http"):
                return self.facebook
            return f"https://facebook.com/{self.facebook.lstrip('@')}"
        return ""

    def get_snapchat_url(self):
        if self.snapchat:
            return f"https://snapchat.com/add/{self.snapchat.lstrip('@')}"
        return ""

    def get_bale_url(self):
        if self.bale:
            if self.bale.startswith("http"):
                return self.bale
            return f"https://ble.ir/{self.bale.lstrip('@')}"
        return ""

    def get_eitaa_url(self):
        if self.eitaa:
            if self.eitaa.startswith("http"):
                return self.eitaa
            return f"https://eitaa.com/{self.eitaa.lstrip('@')}"
        return ""

    def get_gap_url(self):
        if self.gap:
            return f"https://gap.im/{self.gap.lstrip('@')}"
        return ""

    def get_soroush_url(self):
        if self.soroush:
            return f"https://soroush.ir/{self.soroush.lstrip('@')}"
        return ""

    def has_any(self):
        return any([
            self.instagram, self.telegram, self.linkedin,
            self.twitter, self.youtube, self.aparat, self.rubika,
            self.bale, self.eitaa, self.gap, self.soroush,
            self.tiktok, self.pinterest, self.facebook, self.snapchat,
        ])