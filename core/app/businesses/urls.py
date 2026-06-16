from django.urls import path
from .views import (
    index,
    BusinessListView,
    BusinessDetailView,
    AboutView,
    ContactView,
    TermsView,
)

urlpatterns = [
    path("", index, name="home"),

    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("terms/", TermsView.as_view(), name="terms"),

    path("business/", BusinessListView.as_view(), name="business_list"),
    path("<slug:slug>/", BusinessDetailView.as_view(), name="business_detail"),
]