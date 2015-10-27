# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import F
import models_settings
import util
from geopy.distance import distance
from geopy.point import Point


class Token(models.Model):
    token = models.CharField(max_length=32)
    user = models.ForeignKey(User)


class Photo(models.Model):
    file = models.FileField(upload_to=util.getUniquePhotoPath)


class WalkPoint(models.Model):
    walk = models.ForeignKey("Walk")
    time = models.DateTimeField(db_index=True)
    deviceTime = models.DateTimeField(db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    eventCounter = models.PositiveIntegerField(default=0, db_index=True)

    def toDict(self, saved):
        return {
            "walk_id": self.walk_id,
            "time": util.datetimeToTimestmap(self.time),
            "deviceTime": util.datetimeToTimestmap(self.deviceTime),
            "lat": float(self.lat),
            "lon": float(self.lon),
            "saved": saved
        }

    def isSignificantDistance(self, lat, lon):
        return distance(
            Point(float(self.lat), float(self.lon)),
            Point(float(lat), float(lon))
        ).meters >= models_settings.pointsDistanceThreshold


class Walk(models.Model):
    dog = models.ForeignKey("Dog")
    inProgress = models.BooleanField()
    lastTime = models.DateTimeField()

    class Meta:
        index_together = ["dog", "inProgress"]

    def getPathWithinPeriod(self, lowEventCounter, highEventCounter):
        if lowEventCounter is None:
            lowEventCounter = 0
        else:
            lowEventCounter += 1

        walkPoints = WalkPoint.objects.filter(walk=self, eventCounter__gte=lowEventCounter, eventCounter__lte=highEventCounter)
        return [
            {
                "lat": walkPoint.lat,
                "lon": walkPoint.lon,
            } for walkPoint in walkPoints
        ]


class Dog(models.Model):
    nick = models.CharField(max_length=100)
    birthDate = models.DateField(null=True)
    weight = models.IntegerField(null=True)
    user = models.ForeignKey(User)
    avatar = models.CharField(max_length=1000, null=True)
    collarIdHash = models.CharField(max_length=32, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    eventCounter = models.PositiveIntegerField(default=0)

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

    def getWalkInProgress(self):
        time = timezone.now()
        try:
            walkInProgress = Walk.objects.get(dog=self, inProgress=True)
            if (time - walkInProgress.lastTime).seconds > models_settings.walkTimeout:
                walkInProgress.inProgress = False
                walkInProgress.save()
                return None
            else:
                return walkInProgress
        except Walk.DoesNotExist:
            return None

    def checkFinishedWalks(self):
        walkInProgress = self.getWalkInProgress()
        if walkInProgress is None:
            self.lat = self.lon = None
            self.save()
        return walkInProgress

    @classmethod
    def getDogWithIncrementedEventCounter(cls, dog):
        dog.eventCounter = F('eventCounter') + 1
        dog.save()
        dog.refresh_from_db()
        return dog


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


class Achievement(models.Model):
    type = models.PositiveSmallIntegerField()
    dog = models.ForeignKey(Dog)

    def toDict(self):
        return {
            "dog_id": self.dog_id,
            "type": self.type,
        }


class Comment(models.Model):
    dog = models.ForeignKey(Dog)
    text = models.TextField()
    type = models.PositiveSmallIntegerField()  # 0 - text, 1 - walk, 2 - photo, 3 - relation, 4 - achievement
    walk = models.ForeignKey(Walk, null=True)
    photo = models.CharField(max_length=1000, null=True)
    relation = models.ForeignKey(DogRelation, null=True)
    achievement = models.ForeignKey(Achievement, null=True)

    def __unicode__(self):
        return self.text

    def toDict(self):
        result = {
            "id": self.id,
            "dog_id": self.dog_id,
            "text": self.text,
            "type": {
                0: "text",
                1: "walk",
                2: "photo",
                3: "relation",
                4: "achievement",
            }[self.type],
        }

        if self.type == 1:
            result["walk_id"] = self.walk_id
        elif self.type == 2:
            result["photo"] = self.photo
        elif self.type == 3:
            result["relation"] = self.relation.toDict()
        elif self.type == 4:
            result["achievement"] = self.achievement.toDict()

        return result


class Like(models.Model):
    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(User)

    def toDict(self):
        return {
            "comment_id": self.comment_id,
            "user_id": self.user_id,
        }
