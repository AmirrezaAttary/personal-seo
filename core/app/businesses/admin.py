# pages/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Business, BusinessAddress, BusinessSeo, BusinessSocialLinks,
    BusinessTheme, BusinessDocument, BusinessEndorsement, City,
)


# ══════════════════════════════════════════════════════════════════
# Inline ها
# ══════════════════════════════════════════════════════════════════

class BusinessAddressInline(admin.StackedInline):
    model  = BusinessAddress
    extra  = 0
    fieldsets = (
        (None, {
            "fields": (
                ("state", "postal_code"),
                "address_line1", "address_line2",
                ("latitude", "longitude"),
                "google_map_url",
            )
        }),
    )


class BusinessSeoInline(admin.StackedInline):
    model  = BusinessSeo
    extra  = 0
    fieldsets = (
        (None, {
            "fields": ("title", "description", "keywords", "og_image", "robots_index")
        }),
    )


class BusinessSocialLinksInline(admin.StackedInline):
    model  = BusinessSocialLinks
    extra  = 0
    fieldsets = (
        ("پیام‌رسان‌های ایرانی", {
            "fields": ("telegram", "bale", "eitaa", "gap", "soroush", "rubika")
        }),
        ("شبکه‌های ایرانی", {
            "fields": ("instagram", "aparat")
        }),
        ("شبکه‌های بین‌المللی", {
            "fields": ("linkedin", "twitter", "youtube", "tiktok", "pinterest", "facebook", "snapchat")
        }),
    )


class BusinessThemeInline(admin.StackedInline):
    model  = BusinessTheme
    extra  = 0
    fieldsets = (
        ("وضعیت Premium", {
            "fields": ("is_premium", "theme", "font", "tagline"),
        }),
        ("رنگ‌های سفارشی (اختیاری — خالی = پیش‌فرض تم)", {
            "classes": ("collapse",),
            "fields": (
                ("primary_color", "secondary_color"),
                ("background_color", "text_color"),
                "header_bg_image",
            ),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # نمایش پیش‌نمایش رنگ‌ها اگه تم ست شده باشه
        if obj and hasattr(obj, "theme"):
            return ("color_preview",)
        return ()

    readonly_fields = ("color_preview",)

    def color_preview(self, obj):
        if not obj or not obj.pk:
            return "—"
        colors = obj.get_colors()
        swatches = "".join(
            f'<span style="display:inline-block;width:28px;height:28px;border-radius:4px;'
            f'background:{v};margin:2px;border:1px solid #ccc" title="{k}: {v}"></span>'
            for k, v in colors.items()
        )
        return format_html('<div style="display:flex;flex-wrap:wrap;gap:4px">{}</div>', swatches)
    color_preview.short_description = "پیش‌نمایش رنگ‌ها"


class BusinessDocumentInline(admin.TabularInline):
    model   = BusinessDocument
    extra   = 1
    fields  = ("title", "doc_type", "file", "description", "is_public", "order")
    ordering = ("order",)


class BusinessEndorsementInline(admin.StackedInline):
    model   = BusinessEndorsement
    extra   = 0
    fields  = (
        "issuer_name", "issuer_title", "issuer_photo",
        "endorsement_text", "badge_label",
        ("issued_date", "expiry_date"),
        ("is_active", "order"),
    )


# ══════════════════════════════════════════════════════════════════
# BusinessAdmin
# ══════════════════════════════════════════════════════════════════

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name", "activity", "get_city_display_name", "category",
        "premium_badge", "is_verified", "is_active", "created_at",
    )
    list_filter   = ("category", "is_verified", "is_active", "city", "theme__is_premium")
    search_fields = ("name", "activity", "phone", "email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields     = ("qr_code_preview",)

    inlines = [
        BusinessThemeInline,
        BusinessAddressInline,
        BusinessSocialLinksInline,
        BusinessDocumentInline,
        BusinessEndorsementInline,
        BusinessSeoInline,
    ]

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "slug", "category", "logo", "activity", "city", "city_name")
        }),
        ("توضیحات", {
            "fields": ("short_description", "about_text")
        }),
        ("اطلاعات تماس", {
            "fields": ("phone", "whatsapp", "email", "website")
        }),
        ("وضعیت", {
            "fields": ("is_verified", "is_active")
        }),
        ("QR Code", {
            "fields": ("qr_code_preview",),
            "classes": ("collapse",),
        }),
    )

    actions = ["regenerate_qr_codes", "make_premium", "remove_premium"]

    # ─── نمایش badge پرمیوم در لیست ───
    def premium_badge(self, obj):
        try:
            if obj.theme.is_premium:
                label = obj.theme.get_theme_display()
                return format_html(
                    '<span style="background:#C9A84C;color:#000;padding:2px 8px;'
                    'border-radius:10px;font-size:11px;font-weight:700">★ {}</span>',
                    label
                )
        except Exception:
            pass
        return "—"
    premium_badge.short_description = "تم"

    # ─── پیش‌نمایش QR ───
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="width:120px;height:120px;border-radius:8px;'
                'border:1px solid #ddd;padding:6px">',
                obj.qr_code.url
            )
        return "هنوز QR ساخته نشده"
    qr_code_preview.short_description = "QR Code"

    # ─── Actions ───
    @admin.action(description="بازسازی QR Code")
    def regenerate_qr_codes(self, request, queryset):
        count = 0
        for biz in queryset:
            biz.generate_qr_code()
            Business.objects.filter(pk=biz.pk).update(qr_code=biz.qr_code)
            count += 1
        self.message_user(request, f"{count} QR Code با موفقیت بازسازی شد.")

    @admin.action(description="★ تبدیل به کارت لوکس (Gold/Black)")
    def make_premium(self, request, queryset):
        count = 0
        for biz in queryset:
            theme, _ = BusinessTheme.objects.get_or_create(business=biz)
            theme.is_premium = True
            if theme.theme == "default":
                theme.theme = "gold_black"
            theme.save()
            count += 1
        self.message_user(request, f"{count} کسب‌وکار به حالت Premium تبدیل شد.")

    @admin.action(description="حذف حالت Premium")
    def remove_premium(self, request, queryset):
        count = 0
        for biz in queryset:
            try:
                biz.theme.is_premium = False
                biz.theme.save()
                count += 1
            except BusinessTheme.DoesNotExist:
                pass
        self.message_user(request, f"از {count} کسب‌وکار حالت Premium حذف شد.")


# ══════════════════════════════════════════════════════════════════
# City
# ══════════════════════════════════════════════════════════════════

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display  = ("name",)
    search_fields = ("name",)


# ══════════════════════════════════════════════════════════════════
# سایر مدل‌ها (standalone)
# ══════════════════════════════════════════════════════════════════

@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display  = ("title", "business", "doc_type", "is_public", "uploaded_at")
    list_filter   = ("doc_type", "is_public")
    search_fields = ("title", "business__name")
    raw_id_fields = ("business",)


@admin.register(BusinessEndorsement)
class BusinessEndorsementAdmin(admin.ModelAdmin):
    list_display  = ("issuer_name", "issuer_title", "business", "issued_date", "is_active")
    list_filter   = ("is_active",)
    search_fields = ("issuer_name", "business__name")
    raw_id_fields = ("business",)