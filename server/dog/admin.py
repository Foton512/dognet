from django.contrib import admin

class DogAdmin(admin.ModelAdmin):
    list_display = ("nick", "birthDate", "weight", "user", "avatar", "collarIdHash")

class WalkAdmin(admin.ModelAdmin):
    list_display = ("dog", "inProgress")

class WalkPointAdmin(admin.ModelAdmin):
    list_display = ("walk", "time", "deviceTime", "lat", "lon")
