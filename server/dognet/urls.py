# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from dog import models
import dog.admin as admin_models
import views
import settings

admin.site.register(models.Token, admin_models.TokenAdmin)
admin.site.register(models.Dog, admin_models.DogAdmin)
admin.site.register(models.DogRelation, admin_models.DogRelationAdmin)
admin.site.register(models.CloseDogRelation, admin_models.CloseDogRelationAdmin)
admin.site.register(models.CloseDogEvent, admin_models.CloseDogEventAdmin)
admin.site.register(models.UserDogSubscription, admin_models.UserDogSubscriptionAdmin)
admin.site.register(models.Walk, admin_models.WalkAdmin)
admin.site.register(models.WalkPoint, admin_models.WalkPointAdmin)
admin.site.register(models.Home, admin_models.HomeAdmin)
admin.site.register(models.Comment, admin_models.CommentAdmin)
admin.site.register(models.Like, admin_models.LikeAdmin)
admin.site.register(models.Achievement, admin_models.AchievementAdmin)

urlpatterns = [
    # Admin
    url(r"^admin/", include(admin.site.urls)),

    # Authentication
    url(r"^logout/$", "django.contrib.auth.views.logout", {'next_page': '/'}),
    url(r'^auth/(?P<backend>[^/]+)/$', views.auth),
    url('', include('social.apps.django_app.urls', namespace='social')),

    # Site pages
    url(r"^$", views.main),
    url(r"^dog/([0-9]+)/$", views.dog),
    url(r"^dog/edit/([0-9]+)/$", views.edit),
    url(r"^dog/add/$", views.add),
    url(r"^news/$", views.news),
    url(r"^friends/$", views.friends),

    # Api methods
    url(r"^api/dog/add/$", views.addDog),
    url(r"^api/dog/edit/$", views.editDog),
    url(r"^api/dog/get/$", views.getDog),
    url(r"^api/dog/get_list/$", views.getOwnDogs),
    url(r"^api/dog/set_relation/$", views.setDogRelation),
    url(r"^api/dog/subscribe/$", views.subscribe),
    url(r"^api/dog/unsubscribe/$", views.unsubscribe),

    url(r"^api/collar/add_point/$", views.addWalkPoint),

    url(r"^api/user/add_home/$", views.addHome),

    url(r"^api/comment/add_text/$", views.addTextComment),
    url(r"^api/comment/add_photo/$", views.addPhotoComment),
    url(r"^api/comment/del/$", views.deleteComment),
    url(r"^api/comment/like/$", views.like),
    url(r"^api/comment/unlike/$", views.unlike),

    url(r"^api/dog/get_events/$", views.getDogEvents),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
