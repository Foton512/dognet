# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import os
import uuid
import models_settings
import datetime
from django.utils import timezone


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


class WalkPoint(models.Model):
    walk = models.ForeignKey(Walk)
    time = models.DateTimeField(db_index=True)
    deviceTime = models.DateTimeField(db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)


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
            "collar_id_hash": self.collarIdHash
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
