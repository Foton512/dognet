# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import os
import uuid
import models_settings
from social.storage.django_orm import DjangoUserMixin
from django.utils import timezone
import datetime


class Token(models.Model):
    token = models.CharField(max_length=32)
    user = models.ForeignKey(User)


def getUniquePhotoPath(instance, filename):
    return os.path.join("photos", "{}.{}".format(uuid.uuid4(), filename.split(".")[-1]))


class Photo(models.Model):
    file = models.FileField(upload_to=getUniquePhotoPath)


class Walk(models.Model):
    dog = models.ForeignKey("Dog")
    inProgress = models.BooleanField()

    class Meta:
        index_together = ["dog", "inProgress"]


def datetimeToTimestmap(dt):
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


class WalkPoint(models.Model):
    walk = models.ForeignKey(Walk)
    time = models.DateTimeField(db_index=True)
    deviceTime = models.DateTimeField(db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)

    def toDict(self):
        return {
            "walk_id": self.walk_id,
            "time": datetimeToTimestmap(self.time),
            "deviceTime": datetimeToTimestmap(self.deviceTime),
            "lat": float(self.lat),
            "lon": float(self.lon),
        }


def getSocialUrlByUser(user):
    socialUser = DjangoUserMixin.get_social_auth_for_user(user)[0]
    if socialUser.provider == "vk-oauth2":
        return "vk.com/id{}".format(socialUser.uid)
    # TODO: Add facebook


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
            "user_url": getSocialUrlByUser(self.user)
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
            "dog_id": self.dog_id,
            "related_dog_id": self.relatedDog_id,
            "status": self.status,
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
