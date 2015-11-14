# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import F
from django.db import transaction
import models_settings
import util
from geopy.distance import distance
from geopy.point import Point
import sys


class Token(models.Model):
    token = models.CharField(max_length=32)
    user = models.ForeignKey(User)


class CloseDogRelation(models.Model):
    dog = models.ForeignKey("Dog", related_name="+")
    relatedDog = models.ForeignKey("Dog", related_name="+")


class CloseDogEvent(models.Model):
    dog = models.ForeignKey("Dog", related_name="+")
    relatedDog = models.ForeignKey("Dog", related_name="+")
    added = models.BooleanField()  # relatedDog became close if True. Became far otherwise
    status = models.SmallIntegerField(default=0)  # -1 - enemy, 0 - neutral, 1 - friend, 2 - new
    eventCounter = models.PositiveIntegerField(default=0, db_index=True)

    @classmethod
    def removeOldEvents(cls, eventCounter):
        cls.objects.filter(eventCounter__lte=eventCounter - models_settings.closeDogEventsToStore).delete()


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


class Walk(models.Model):
    dog = models.ForeignKey("Dog")
    inProgress = models.BooleanField()
    lastTime = models.DateTimeField()
    length = models.FloatField(default=0)

    class Meta:
        index_together = ["dog", "inProgress"]

    def getPathWithinPeriod(self, lowEventCounter, highEventCounter):
        if lowEventCounter is None:
            lowEventCounter = 0
        else:
            lowEventCounter += 1

        walkPoints = WalkPoint.objects.filter(walk=self,
                                              eventCounter__gte=lowEventCounter,
                                              eventCounter__lte=highEventCounter).order_by("eventCounter")
        return [
            {
                "lat": walkPoint.lat,
                "lon": walkPoint.lon,
            } for walkPoint in walkPoints
        ]

    def getPath(self):
        walkPoints = WalkPoint.objects.filter(walk=self)
        return [
            (float(point.lat), float(point.lon)) for point in walkPoints
        ]

    def getCenter(self):
        walkPoints = WalkPoint.objects.filter(walk=self)
        xPoints = [float(point.lat) for point in walkPoints]
        yPoints = [float(point.lon) for point in walkPoints]
        xMean = reduce(lambda x, y: x + y, xPoints) / len(xPoints)
        yMean = reduce(lambda x, y: x + y, yPoints) / len(yPoints)
        return [xMean, yMean]

    def toDict(self):
        return {
            "dog": self.dog.toDict(),
            "in_progress": self.inProgress,
            "length": self.length,
            "path": self.getPath(),
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


class Comment(models.Model):
    dog = models.ForeignKey("Dog")
    text = models.TextField()
    type = models.PositiveSmallIntegerField()  # 0 - text, 1 - walk, 2 - photo, 3 - relation, 4 - achievement
    walk = models.ForeignKey("Walk", null=True)
    photoFile = models.FileField(upload_to=util.getUniquePhotoPath, null=True)
    relation = models.ForeignKey("DogRelation", null=True)
    achievement = models.ForeignKey("Achievement", null=True)
    eventCounter = models.PositiveIntegerField(default=0, db_index=True)
    time = models.DateTimeField(auto_now_add=True)
    parentComment = models.ForeignKey("Comment", null=True)

    def __unicode__(self):
        return self.text

    def toDict(self):
        result = {
            "id": self.id,
            "dog": self.dog.toDict(),
            "dog_id": self.dog_id,
            "nick": self.dog.nick,
            "avatar": self.dog.avatarFile.url if self.dog.avatarFile else None,
            "text": self.text,
            "type": {
                0: "text",
                1: "walk",
                2: "photo",
                3: "relation",
                4: "achievement",
            }[self.type],
            "parent_comment_id": self.parentComment_id if self.parentComment else None,
        }

        if self.type == 1:
            result["walk"] = self.walk.toDict()
        elif self.type == 2:
            result["photo"] = self.photoFile.url if self.photoFile else None
        elif self.type == 3:
            result["relation"] = self.relation.toDict()
        elif self.type == 4:
            result["achievement"] = self.achievement.toDict()

        return result


class State(models.Model):
    eventCounter = models.PositiveIntegerField(default=0)

    # relatedObjects must not be not saved yet
    def incEventCounter(self, relatedObjects):
        with transaction.atomic():
            self.eventCounter = F('eventCounter') + 1
            self.save()
            self.refresh_from_db(fields=["eventCounter"])
            for obj in relatedObjects:
                obj.eventCounter = self.eventCounter
                obj.save()

    @classmethod
    def getState(cls):
        with transaction.atomic():
            state = cls.objects.get_or_create(id=1)[0]
        return state


class Dog(models.Model):
    nick = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, null=True)
    birthDate = models.DateField(null=True)
    weight = models.FloatField(null=True)
    user = models.ForeignKey(User)
    avatarFile = models.FileField(upload_to=util.getUniquePhotoPath, null=True)
    collarIdHash = models.CharField(max_length=32, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    totalWalkLength = models.FloatField(default=0)

    def __unicode__(self):
        return self.nick

    def toDict(self):
        return {
            "id": self.id,
            "breed": self.breed,
            "nick": self.nick,
            "birth_date": self.birthDate.strftime("%Y%m%d") if self.birthDate else "",
            "weight": self.weight,
            "collar_id_hash": self.collarIdHash,
            "user_first_name": self.user.first_name,
            "user_second_name": self.user.last_name,
            "user_url": util.getSocialUrlByUser(self.user),
            "on_walk": Walk.objects.filter(dog=self, inProgress=True).exists(),
            "avatar": self.avatarFile.url if self.avatarFile else None,
            "lat": self.lat,
            "lon": self.lon,
            "total_walk_length": self.totalWalkLength
        }

    def getWalkInProgress(self):
        time = timezone.now()
        try:
            walkInProgress = Walk.objects.get(dog=self, inProgress=True)
            if (time - walkInProgress.lastTime).seconds > models_settings.walkTimeout:
                nearestHome = self.getNearestHome()
                if nearestHome:
                    lastWalkPoint = WalkPoint.objects.filter(walk=walkInProgress).latest("id")
                    self.createWalkPoint(
                        walkInProgress,
                        time,
                        lastWalkPoint.deviceTime,
                        nearestHome.lat,
                        nearestHome.lon
                    )
                walkInProgress.inProgress = False
                walkInProgress.save()

                comment = Comment(dog=self, text="", type=1, walk=walkInProgress)
                State.getState().incEventCounter([comment])

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

    def createWalkPoint(self, walk, time, deviceTime, lat, lon):
        walkPoint = WalkPoint(
            walk=walk,
            time=time,
            deviceTime=deviceTime,
            lat=lat,
            lon=lon
        )
        State.getState().incEventCounter([walkPoint])

    def getNearestHome(self):
        nearestHome = None
        homes = Home.objects.filter(user=self.user)
        if self.lat and self.lon and homes.exists():
            minDistance = sys.float_info.max
            for home in homes:
                homeDistance = distance(Point(self.lat, self.lon), Point(home.lat, home.lon)).meters
                if homeDistance < minDistance and homeDistance < models_settings.homeDistanceThreshold:
                    minDistance = homeDistance
                    nearestHome = home
        return nearestHome


class DogRelation(models.Model):
    dog = models.ForeignKey(Dog, related_name="+")
    relatedDog = models.ForeignKey(Dog, related_name="+")
    status = models.SmallIntegerField(default=0)  # -1 - enemy, 0 - neutral, 1 - friend

    def toDict(self):
        return {
            "id": self.dog_id,
            "related_id": self.relatedDog_id,
            "dog": self.dog.toDict(),
            "related_dog": self.relatedDog.toDict(),
            "status": self.status,
        }


class UserDogSubscription(models.Model):
    user = models.ForeignKey(User)
    dog = models.ForeignKey(Dog)

    def toDict(self):
        return {
            "user_id": self.user_id,
            "dog_id": self.dog_id,
            "dog": self.dog.toDict(),
        }


class Like(models.Model):
    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(User)
    eventCounter = models.PositiveIntegerField(default=0, db_index=True)

    def toDict(self):
        return {
            "comment_id": self.comment_id,
            "user_id": self.user_id,
            "comment": self.comment.toDict(),
        }


class Achievement(models.Model):
    type = models.PositiveSmallIntegerField()  # 1 - First friend
                                               # 2 - First enemy
                                               # 3 - 50m length distance
    dog = models.ForeignKey(Dog)
    eventCounter = models.PositiveIntegerField(default=0)

    def getDescription(self):
        return {
            1: u"Завел своего первого друга!",
            2: u"Нажил первого врага!",
            3: u"Преодолел 50 метров!",
            4: u"Первая прогулка!",
        }[self.type]

    def toDict(self):
        return {
            "dog_id": self.dog_id,
            "dog": self.dog.toDict(),
            "type": self.type,
            "description": self.getDescription(),
        }

    @classmethod
    def addAchievement(cls, type, dog):
        if cls.objects.filter(dog=dog, type=type).exists():
            return
        achievement = cls(dog=dog, type=type)
        State.getState().incEventCounter([achievement])
        comment = Comment(dog=dog, text="", type=4, achievement=achievement)
        State.getState().incEventCounter([comment])
