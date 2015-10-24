from django.contrib import admin


class DogAdmin(admin.ModelAdmin):
    list_display = ("nick", "birthDate", "weight", "user", "avatar", "collarIdHash")


class DogRelationAdmin(admin.ModelAdmin):
    list_display = ("dog", "relatedDog", "status")


class WalkAdmin(admin.ModelAdmin):
    list_display = ("dog", "inProgress")


class WalkPointAdmin(admin.ModelAdmin):
    list_display = ("walk", "time", "deviceTime", "lat", "lon")


class HomeAdmin(admin.ModelAdmin):
    list_display = ("user", "lat", "lon")
