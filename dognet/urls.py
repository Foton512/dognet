from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^$", views.main),
    url(r"^dog/([0-9]+)/$", views.dog),
]
