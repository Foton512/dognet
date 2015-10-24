# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import models_settings
from django.utils import timezone
import util


class Token(models.Model):
    token = models.CharField(max_length=32)
    user = models.ForeignKey(User)


class Photo(models.Model):
    file = models.FileField(upload_to=util.getUniquePhotoPath)


class Walk(models.Model):
    dog = models.ForeignKey("Dog")
    inProgress = models.BooleanField()

    class Meta:
        index_together = ["dog", "inProgress"]


class WalkPoint(models.Model):
    walk = models.ForeignKey(Walk)
    time = models.DateTimeField(db_index=True)
    deviceTime = models.DateTimeField(db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)

    def toDict(self):
        return {
            "walk_id": self.walk_id,
            "time": util.datetimeToTimestmap(self.time),
            "deviceTime": util.datetimeToTimestmap(self.deviceTime),
            "lat": float(self.lat),
            "lon": float(self.lon),
        }


class Dog(models.Model):
    nick = models.CharField(max_length=100)
    birthDate = models.DateField(null=True)
    weight = models.IntegerField(null=True)
    user = models.ForeignKey(User)
    avatar = models.CharField(max_length=1000, null=True)
    collarIdHash = models.CharField(max_length=32, null=True)

    def __unicode__(self):
        return self.nick

    def toDict(self):
        return {
            "id": self.id,
            "nick": self.nick,
            "birth_date": self.birthDate.strftime("%Y%m%d") if self.birthDate else "",
            "weight": self.weight,
            "avatar": self.avatar,
            "collar_id_hash": self.collarIdHash,
            "user_first_name": self.user.first_name,
            "user_second_name": self.user.last_name,
            "user_url": util.getSocialUrlByUser(self.user),
            "on_walk": Walk.objects.filter(dog=self, inProgress=True).exists(),
        }

    def checkFinishedWalks(self):
        time = timezone.now()
        try:
            walkInProgress = Walk.objects.get(dog=self, inProgress=True)
            lastWalkPoint = WalkPoint.objects.filter(walk=walkInProgress).latest("time")
            if (time - lastWalkPoint.time).seconds > models_settings.walkTimeout:
                walkInProgress.inProgress = False
                walkInProgress.save()
                return None
            else:
                return walkInProgress
        except Walk.DoesNotExist:
            return None


class DogRelation(models.Model):
    dog = models.ForeignKey(Dog, related_name="+")
    relatedDog = models.ForeignKey(Dog, related_name="+")
    status = models.SmallIntegerField(default=0)  # -1 - enemy, 0 - neutral, 1 - friend

    def toDict(self):
        return {
            "id": self.dog_id,
            "related_id": self.relatedDog_id,
            "status": self.status,
        }


class UserDogSubscription(models.Model):
    user = models.ForeignKey(User)
    dog = models.ForeignKey(Dog)

    def toDict(self):
        return {
            "user_id": self.user_id,
            "dog_id": self.dog_id,
        }


class Home(models.Model):
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    user = models.ForeignKey(User)

    def toDict(self):
        return {
            "user_id": self.user_id,
            "lat": self.lat,
            "lon": self.lon,
        }
