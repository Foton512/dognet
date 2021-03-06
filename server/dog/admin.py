from django.contrib import admin


class TokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token")


class WalkAdmin(admin.ModelAdmin):
    list_display = ("dog", "inProgress")


class CloseDogRelationAdmin(admin.ModelAdmin):
    list_display = ("dog", "relatedDog")


class CloseDogEventAdmin(admin.ModelAdmin):
    list_display = ("dog", "relatedDog", "status", "eventCounter")


class WalkPointAdmin(admin.ModelAdmin):
    list_display = ("walk", "time", "deviceTime", "lat", "lon")


class DogAdmin(admin.ModelAdmin):
    list_display = ("nick", "birthDate", "weight", "user", "avatarFile", "collarIdHash")


class DogRelationAdmin(admin.ModelAdmin):
    list_display = ("dog", "relatedDog", "status")


class UserDogSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "dog")


class HomeAdmin(admin.ModelAdmin):
    list_display = ("user", "lat", "lon")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "type", "parentComment")


class LikeAdmin(admin.ModelAdmin):
    list_display = ("comment", "user")


class AchievementAdmin(admin.ModelAdmin):
    list_display = ("type", "dog")
