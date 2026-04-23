from django.urls import path
from .views import index ,BusinessListView, BusinessDetailView

urlpatterns = [
    path("", index, name="home"),
    path("business/", BusinessListView.as_view(), name="business_list"),
    path("business/<slug:slug>/", BusinessDetailView.as_view(), name="business_detail"),
]