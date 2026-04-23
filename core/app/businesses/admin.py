# pages/admin.py
from django.contrib import admin
from .models import Business, BusinessAddress, BusinessSeo, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class BusinessAddressInline(admin.StackedInline):
    model = BusinessAddress
    extra = 0


class BusinessSeoInline(admin.StackedInline):
    model = BusinessSeo
    extra = 0


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "activity", "get_city_display", "phone", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "activity", "phone", "email", "city_name")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "slug", "category", "activity", "city", "city_name", "short_description", "about_text", "is_active")
        }),
        ("اطلاعات تماس", {
            "fields": ("phone", "whatsapp", "email"),
        }),
    )

    inlines = [BusinessAddressInline, BusinessSeoInline]


@admin.register(BusinessAddress)
class BusinessAddressAdmin(admin.ModelAdmin):
    list_display = ("business", "state", "address_line1", "postal_code")
    search_fields = ("business__name", "address_line1", "state", "postal_code")


@admin.register(BusinessSeo)
class BusinessSeoAdmin(admin.ModelAdmin):
    list_display = ("business", "title", "robots_index")
    search_fields = ("business__name", "title", "description", "keywords")
