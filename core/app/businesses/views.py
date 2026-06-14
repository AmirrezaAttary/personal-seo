from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import Business, City


def index(request):
    city     = request.GET.get("city", "").strip()
    activity = request.GET.get("activity", "").strip()

    qs = (
        Business.objects
        .filter(is_active=True)
        .select_related("city", "seo", "address")
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
    model                = Business
    template_name        = "businesses/business_list.html"
    context_object_name  = "businesses"
    paginate_by          = 12

    def get_queryset(self):
        qs = (
            Business.objects
            .filter(is_active=True)
            .select_related("city", "seo")
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
        ctx["filter_city"]      = self.request.GET.get("city", "").strip()
        ctx["filter_activity"]  = self.request.GET.get("activity", "").strip()
        ctx["filter_category"]  = self.request.GET.get("category", "").strip()
        return ctx


class BusinessDetailView(DetailView):
    model               = Business
    template_name       = "businesses/business_detail.html"
    context_object_name = "business"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return Business.objects.filter(is_active=True).select_related("city", "seo", "address")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["seo"]     = getattr(self.object, "seo", None)
        ctx["address"] = getattr(self.object, "address", None)
        return ctx