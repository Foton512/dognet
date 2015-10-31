# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from dog import models, models_settings
from social.apps.django_app.utils import psa
import uuid
import view_decorators
import forms
import hashlib
import datetime
from django.utils import timezone
from decimal import Decimal
import geopy
from geopy.distance import distance
from geopy.point import Point


def main(request):
    user = request.user
    if user.is_authenticated():
        return redirect("/dogs/")
    else:
        return redirect("/login/")


def login(request):
    return render_to_response("login.html")


@psa('social:complete')
def auth(request, backend):
    socialToken = request.GET.get('access_token')
    user = request.backend.do_auth(socialToken)
    token = models.Token.objects.create(token=uuid.uuid4().hex, user=user)
    return JsonResponse({
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "access_token": token.token,
    })


def dogs(request):
    user = request.user
    dogs = models.Dog.objects.filter(user=user)
    return render_to_response(
        "dogs.html",
        context={
            "user": user,
            "dogs": dogs,
            "photoForm": forms.PhotoForm(),
        },
        context_instance=RequestContext(request)
    )


def dog(request, dogId):
    dog = models.Dog.objects.get(id=dogId)

    return render_to_response(
        "dog.html",
        context={
            "nick": dog.nick,
            "birthDate": dog.birthDate.strftime("%Y%m%d"),
            "weight": dog.weight,
            "avatar": dog.avatar,
        },
    )


def uploadPhoto(request):
    photo = models.Photo.objects.create(file=request.FILES["photoFile"])
    return JsonResponse({"url": photo.file.url})


@view_decorators.apiLoginRequired
def addDog(request):
    params = request.GET
    birthDate = datetime.datetime.strptime(params["birth_date"], "%Y%m%d") if "birth_date" in params else None
    dog = models.Dog.objects.create(
        nick=params["nick"],
        birthDate=birthDate,
        weight=params.get("weight", None),
        user=request.user,
        avatar=params.get("avatar", None),
        collarIdHash=hashlib.md5(params["collar_id"]).hexdigest() if "collar_id" in params else None
    )
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def editDog(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    dog.checkFinishedWalks()
    if "nick" in params:
        dog.nick = params["nick"]
    if "birth_date" in params:
        birthDate = params["birth_date"]
        if birthDate:
            birthDate = datetime.strptime(birthDate, "%Y%m%d")
        else:
            birthDate = None
        dog.birthDate = birthDate
    if "weight" in params:
        weight = params["weight"]
        dog.weight = int(weight) if weight else None
    if "avatar" in params:
        avatar = params["avatar"]
        dog.avatar = avatar if avatar else None
    if "collar_id" in params:
        collarId = params["collar_id"]
        dog.collarIdHash = hashlib.md5(collarId).hexdigest() if collarId else None
    dog.save()
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def getDog(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    dog.checkFinishedWalks()
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def getOwnDogs(request):
    dogs = models.Dog.objects.filter(user=request.user)
    for dog in dogs:
        dog.checkFinishedWalks()
    return JsonResponse([dog.toDict() for dog in dogs], safe=False)


@view_decorators.apiLoginRequired
def setDogRelation(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    relatedDog = models.Dog.objects.get(id=params["related_id"])
    relation = models.DogRelation.objects.get_or_create(dog=dog, relatedDog=relatedDog)[0]
    relation.status = int(params["status"])
    relation.save()
    return JsonResponse(relation.toDict())


@view_decorators.apiLoginRequired
def subscribe(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    subscription = models.UserDogSubscription.objects.get_or_create(user=request.user, dog=dog)[0]
    return JsonResponse(subscription.toDict())


@view_decorators.apiLoginRequired
def unsubscribe(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    subscription = models.UserDogSubscription.objects.get(user=request.user, dog=dog)
    response = subscription.toDict()
    subscription.delete()
    return JsonResponse(response)


@view_decorators.apiLoginRequired
def addHome(request):
    params = request.GET
    home = models.Home.objects.create(user=request.user, lat=Decimal(params["lat"]), lon=Decimal(params["lon"]))
    return JsonResponse(home.toDict())


def getDogStatus(dogId, dogIdToStatus):
    return dogIdToStatus.get(dogId, 2)


def addCloseDogEvents(dog, relatedDogs, added):
    relatedDogIdToStatus = {
        dogRelation.relatedDog_id: dogRelation.status
        for dogRelation in models.DogRelation.objects.filter(dog=dog, relatedDog__in=relatedDogs)
    }
    for relatedDog in relatedDogs:
        closeDogEvent = models.CloseDogEvent(
            dog=dog,
            relatedDog=relatedDog,
            added=added,
            status=getDogStatus(relatedDog.id, relatedDogIdToStatus)
        )
        dog.incEventCounter([closeDogEvent])


def addWalkPoint(request):
    try:
        time = timezone.now()
        params = request.GET
        collarIdHash = params["collar_id_hash"]

        dog = models.Dog.objects.get(collarIdHash=collarIdHash)
        walkInProgress = dog.checkFinishedWalks()

        lat = Decimal(params["lat"])
        lon = Decimal(params["lon"])
        dog.lat = lat
        dog.lon = lon

        createNewWalkPoint = False
        if walkInProgress is None:
            walkInProgress = models.Walk.objects.create(dog=dog, inProgress=True, lastTime=time)
            createNewWalkPoint = True
            # TODO: add first point in nearest house
        else:
            lastWalkPoint = models.WalkPoint.objects.filter(walk=walkInProgress).latest("eventCounter")
            if lastWalkPoint.isSignificantDistance(lat, lon):
                createNewWalkPoint = True

        if createNewWalkPoint:
            walkPoint = models.WalkPoint(
                walk=walkInProgress,
                time=time,
                deviceTime=datetime.datetime.fromtimestamp(int(params["timestamp"])).replace(tzinfo=None),
                lat=lat,
                lon=lon
            )
            dog.incEventCounter([walkPoint])

        approxDistanceThreshold = geopy.units.degrees(arcminutes=geopy.units.nautical(miles=1))
        closeCandidates = models.Dog.objects.filter(
            ~Q(id=dog.id),
            lat__range=(float(lat) - approxDistanceThreshold, float(lat) + approxDistanceThreshold),
            lon__range=(float(lon) - approxDistanceThreshold, float(lon) + approxDistanceThreshold)
        )
        newCloseDogs = [
            closeCandidate for closeCandidate in closeCandidates if distance(
                Point(lat, lon),
                Point(closeCandidate.lat, closeCandidate.lon)
            ) <= models_settings.pointsDistanceThreshold
        ]
        oldCloseDogs = [
            closeDogRelation.relatedDog for closeDogRelation in models.CloseDogRelation.objects.filter(dog=dog)
        ]

        dogsAdded = set(newCloseDogs) - set(oldCloseDogs)
        dogsRemoved = set(oldCloseDogs) - set(newCloseDogs)
        for relatedDog in dogsAdded:
            models.CloseDogRelation.objects.create(dog=dog, relatedDog=relatedDog)
        addCloseDogEvents(dog, dogsAdded, True)
        models.CloseDogRelation.objects.filter(dog=dog, relatedDog__in=dogsRemoved).delete()
        addCloseDogEvents(dog, dogsRemoved, False)

        models.CloseDogEvent.removeOldEvents(dog.eventCounter)
    except Exception as e:
        return JsonResponse({"error": str(e)})

    return JsonResponse({})


@view_decorators.apiLoginRequired
def addTextComment(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    comment = models.Comment.objects.create(dog=dog, text=params["text"], type=0)
    return JsonResponse(comment.toDict())


@view_decorators.apiLoginRequired
def addPhotoComment(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    comment = models.Comment.objects.create(dog=dog, text=params["text"], photo=params["photo"], type=2)
    return JsonResponse(comment.toDict())


@view_decorators.apiLoginRequired
def deleteComment(request):
    params = request.GET
    comment = models.Comment.objects.get(id=params["comment_id"])
    if comment.dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    response = comment.toDict()
    comment.delete()
    return JsonResponse(response)


@view_decorators.apiLoginRequired
def like(request):
    params = request.GET
    like = models.Like.objects.get_or_create(comment_id=params["comment_id"], user=request.user)[0]
    return JsonResponse(like.toDict())


@view_decorators.apiLoginRequired
def unlike(request):
    params = request.GET
    like = models.Like.objects.get(comment_id=params["comment_id"], user=request.user)
    response = like.toDict()
    like.delete()
    return JsonResponse(response)


@view_decorators.apiLoginRequired
def getDogEvents(request):
    params = request.GET
    eventCounter = int(params["event_counter"]) if "event_counter" in params else None
    fields = params["fields"].split(",")
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    response = {
        "dog_id": dog.id,
        "event_counter": dog.eventCounter,
    }

    if "lat" in fields or "lon" in fields or "walk" in fields:
        walkInProgress = dog.checkFinishedWalks()

    if "lat" in fields:
        response["lat"] = float(dog.lat) if dog.lat else None
    if "lon" in fields:
        response["lon"] = float(dog.lon) if dog.lon else None
    if "walk" in fields:
        response["walk"] = {
            "id": walkInProgress.id,
            "path": walkInProgress.getPathWithinPeriod(eventCounter, dog.eventCounter),
        } if walkInProgress else None
    if "close_dogs_events" in fields:
        if eventCounter:
            closeDogEvents = models.CloseDogEvent.objects.filter(dog=dog,
                                                                 eventCounter__gt=eventCounter).order_by("eventCounter")
            response["close_dogs_events"] = [
                {
                    "dog_id": closeDogEvent.relatedDog_id,
                    "became_close": closeDogEvent.added,
                    "status": closeDogEvent.status,
                } for closeDogEvent in closeDogEvents
            ]
        else:
            closeDogRelations = models.CloseDogRelation.objects.filter(dog=dog)
            closeDogIds = [
                closeDogRelation.relatedDog.id for closeDogRelation in closeDogRelations
            ]
            closeDogIdToStatus = {
                dogRelation.relatedDog_id: dogRelation.status
                for dogRelation in models.DogRelation.objects.filter(dog=dog, relatedDog__in=closeDogIds)
            }
            response["close_dogs_events"] = [
                {
                    "dog_id": closeDogRelation.relatedDog_id,
                    "became_close": True,
                    "status": getDogStatus(closeDogRelation.relatedDog_id, closeDogIdToStatus)
                } for closeDogRelation in closeDogRelations
            ]

    return JsonResponse(response)