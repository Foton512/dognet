from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^login/$", views.login),
    url(r"^logout/$", "django.contrib.auth.views.logout", {'next_page': '/'}),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r"^$", views.main),
    url(r"^dog/([0-9]+)/$", views.dog),

    url(r"^api/dog/add/$", views.addDog),
    url(r"^api/dog/edit/$", views.editDog),
    url(r"^api/dog/get/$", views.getDog),
]
