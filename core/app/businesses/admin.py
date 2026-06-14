# pages/admin.py
from django.contrib import admin
from .models import Business, BusinessAddress, BusinessSeo, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display  = ("name",)
    search_fields = ("name",)


class BusinessAddressInline(admin.StackedInline):
    model = BusinessAddress
    extra = 0


class BusinessSeoInline(admin.StackedInline):
    model = BusinessSeo
    extra = 0


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "activity",
        "city_display",          # متد زیر — جایگزین get_city_display
        "phone", "is_verified", "is_active", "created_at",
    )
    list_filter       = ("category", "is_active", "is_verified", "created_at")
    search_fields     = ("name", "activity", "phone", "email", "city_name", "city__name")
    prepopulated_fields = {"slug": ("name",)}
    ordering          = ("-created_at",)
    list_editable     = ("is_active", "is_verified")

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "name", "slug", "category", "logo",
                "activity", "city", "city_name",
                "short_description", "about_text",
                "is_active", "is_verified",
            )
        }),
        ("اطلاعات تماس", {
            "fields": ("phone", "whatsapp", "email", "website"),
        }),
    )

    inlines = [BusinessAddressInline, BusinessSeoInline]

    @admin.display(description="شهر")
    def city_display(self, obj):
        return obj.get_city_display_name()