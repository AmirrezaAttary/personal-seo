# pages/admin.py
from django.contrib import admin
from .models import Business, BusinessAddress, BusinessSeo, BusinessSocialLinks, City


class BusinessAddressInline(admin.StackedInline):
    model = BusinessAddress
    extra = 0


class BusinessSeoInline(admin.StackedInline):
    model = BusinessSeo
    extra = 0


class BusinessSocialLinksInline(admin.StackedInline):
    model = BusinessSocialLinks
    extra = 0
    fieldsets = (
        ("شبکه‌های اجتماعی ایرانی", {
            "fields": ("telegram", "aparat", "rubika")
        }),
        ("شبکه‌های اجتماعی بین‌المللی", {
            "fields": ("instagram", "linkedin", "twitter", "youtube")
        }),
    )


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display  = ("name", "activity", "get_city_display_name", "category", "is_verified", "is_active", "created_at")
    list_filter   = ("category", "is_verified", "is_active", "city")
    search_fields = ("name", "activity", "phone", "email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("qr_code",)

    inlines = [BusinessAddressInline, BusinessSocialLinksInline, BusinessSeoInline]

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
        ("QR Code (خودکار)", {
            "fields": ("qr_code",),
            "classes": ("collapse",),
        }),
    )

    actions = ["regenerate_qr_codes"]

    def regenerate_qr_codes(self, request, queryset):
        count = 0
        for biz in queryset:
            biz.generate_qr_code()
            Business.objects.filter(pk=biz.pk).update(qr_code=biz.qr_code)
            count += 1
        self.message_user(request, f"{count} QR Code با موفقیت بازسازی شد.")
    regenerate_qr_codes.short_description = "بازسازی QR Code"


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display  = ("name",)
    search_fields = ("name",)