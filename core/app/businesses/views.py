# pages/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Business, City


def index(request):
    city     = request.GET.get("city", "").strip()
    activity = request.GET.get("activity", "").strip()

    qs = (
        Business.objects
        .filter(is_active=True)
        .select_related("city", "seo", "address", "theme")
        .order_by("-created_at")
    )

    if city:
        qs = qs.filter(Q(city__name__icontains=city) | Q(city_name__icontains=city))
    if activity:
        qs = qs.filter(activity__icontains=activity)

    stats = {
        "total":  Business.objects.filter(is_active=True).count(),
        "cities": City.objects.filter(businesses__is_active=True).distinct().count(),
    }

    categories = [
        {"icon": "ti-building-store", "label": "مغازه و فروشگاه", "value": "shop"},
        {"icon": "ti-briefcase",      "label": "شرکت",             "value": "company"},
        {"icon": "ti-user",           "label": "فریلنسر / شخص",   "value": "person"},
        {"icon": "ti-tools",          "label": "خدمات",            "value": "service"},
    ]

    return render(request, "businesses/index.html", {
        "latest_businesses": qs[:9],
        "filter_city":       city,
        "filter_activity":   activity,
        "stats":             stats,
        "categories":        categories,
    })


class BusinessListView(ListView):
    model               = Business
    template_name       = "businesses/business_list.html"
    context_object_name = "businesses"
    paginate_by         = 12

    def get_queryset(self):
        qs = (
            Business.objects
            .filter(is_active=True)
            .select_related("city", "seo", "theme")
            .order_by("-created_at")
        )
        city     = self.request.GET.get("city", "").strip()
        activity = self.request.GET.get("activity", "").strip()
        category = self.request.GET.get("category", "").strip()

        if city:
            qs = qs.filter(Q(city__name__icontains=city) | Q(city_name__icontains=city))
        if activity:
            qs = qs.filter(activity__icontains=activity)
        if category:
            qs = qs.filter(category=category)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_city"]     = self.request.GET.get("city", "").strip()
        ctx["filter_activity"] = self.request.GET.get("activity", "").strip()
        ctx["filter_category"] = self.request.GET.get("category", "").strip()
        return ctx


class BusinessDetailView(DetailView):
    model               = Business
    context_object_name = "business"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            Business.objects
            .filter(is_active=True)
            .select_related("city", "seo", "address", "social", "theme")
            .prefetch_related("documents", "endorsements")
        )

    def get_template_names(self):
        """
        اگه کارت ویزیت Premium باشه، تمپلیت لوکس لود میشه.
        در غیر این صورت تمپلیت پیش‌فرض.
        """
        try:
            if self.object.theme.is_premium:
                return ["businesses/business_detail_premium.html"]
        except Exception:
            pass
        return ["businesses/business_detail.html"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["seo"]          = getattr(self.object, "seo",    None)
        ctx["address"]      = getattr(self.object, "address", None)
        ctx["social"]       = getattr(self.object, "social",  None)
        ctx["theme"]        = getattr(self.object, "theme",   None)
        ctx["documents"]    = self.object.documents.filter(is_public=True)
        ctx["endorsements"] = self.object.endorsements.filter(is_active=True)

        # رنگ‌های تم برای CSS variables
        if ctx["theme"]:
            ctx["theme_colors"] = ctx["theme"].get_colors()
        else:
            ctx["theme_colors"] = None

        return ctx


class AboutView(TemplateView):
    template_name = "businesses/about.html"


class ContactView(TemplateView):
    template_name = "businesses/contact.html"


class TermsView(TemplateView):
    template_name = "businesses/terms.html"