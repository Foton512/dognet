# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from dog import models
import dog.admin as admin_models
import views
import settings

admin.site.register(models.Dog, admin_models.DogAdmin)
admin.site.register(models.Walk, admin_models.WalkAdmin)
admin.site.register(models.WalkPoint, admin_models.WalkPointAdmin)

urlpatterns = [
    # Admin
    url(r"^admin/", include(admin.site.urls)),

    # Authentication
    url(r"^login/$", views.login),
    url(r"^logout/$", "django.contrib.auth.views.logout", {'next_page': '/'}),
    url(r'^auth/(?P<backend>[^/]+)/$', views.auth),
    url('', include('social.apps.django_app.urls', namespace='social')),

    # Site pages
    url(r"^$", views.main),
    url(r"^dogs/$", views.dogs),
    url(r"^dog/([0-9]+)/$", views.dog),

    # File upload
    url(r"^upload_photo/$", views.uploadPhoto),

    # Api methods
    url(r"^api/dog/add/$", views.addDog),
    url(r"^api/dog/edit/$", views.editDog),
    url(r"^api/dog/get/$", views.getDog),

    url(r"^api/collar/add_point/$", views.addWalkPoint),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
