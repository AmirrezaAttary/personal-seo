from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Business
from django.db.models import Q

def index(request):
    city = request.GET.get("city", "").strip()
    activity = request.GET.get("activity", "").strip()

    qs = Business.objects.filter(is_active=True).select_related("city", "seo").order_by("-created_at")

    if city:
        qs = qs.filter(Q(city__name__icontains=city) | Q(city_name__icontains=city))
    if activity:
        qs = qs.filter(activity__icontains=activity)

    latest = qs[:8]  # تعداد کارت‌های روی صفحه

    return render(request, "businesses/index.html", {
        "latest_businesses": latest,
        "filter_city": city,
        "filter_activity": activity,
    })


class BusinessListView(ListView):
    model = Business
    template_name = "businesses/business_list.html"
    context_object_name = "businesses"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Business.objects
            .filter(is_active=True)
            .select_related("city", "seo")
            .order_by("-created_at")
        )

        city = self.request.GET.get("city", "").strip()
        activity = self.request.GET.get("activity", "").strip()

        if city:
            # اگر City مدل داری، با city__name فیلتر می‌کنیم
            # و اگر کاربر چیزی مثل "تهران" وارد کرد ولی City نداری، fallback داریم به city_name
            qs = qs.filter(Q(city__name__icontains=city) | Q(city_name__icontains=city))

        if activity:
            qs = qs.filter(activity__icontains=activity)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        city = self.request.GET.get("city", "").strip()
        activity = self.request.GET.get("activity", "").strip()

        # لیست‌های فیلتر برای dropdown (اختیاری ولی بهتره)
        ctx["filter_city"] = city
        ctx["filter_activity"] = activity

        # گزینه‌های شهر: اگر City نداری، این لیست ممکنه خالی/کم باشد
        ctx["cities"] = (
            Business.objects
            .filter(is_active=True)
            .values_list("city__name", flat=True)
            .distinct()
        )

        # حوزه فعالیت‌های یکتا (برای dropdown سبک)
        ctx["activities"] = (
            Business.objects
            .filter(is_active=True)
            .values_list("activity", flat=True)
            .distinct()
        )

        return ctx


class BusinessDetailView(DetailView):
    model = Business
    template_name = "businesses/business_detail.html"
    context_object_name = "business"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Business.objects
            .select_related("city", "seo", "address")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        business = self.object

        ctx["seo"] = getattr(business, "seo", None)
        ctx["address"] = getattr(business, "address", None)
        ctx["now_year"] = __import__("datetime").datetime.now().year

        return ctx
