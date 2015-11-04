# -*- coding: utf-8 -*-
import uuid
import hashlib
import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from social.apps.django_app.utils import psa
from django.utils import timezone
import geopy
from geopy.distance import distance
from geopy.point import Point

from dog import models, models_settings, forms
import view_decorators
from date_util import dateToStr, dateFromStr


def main(request):
    user = request.user
    if user.is_authenticated():
        return redirect("/dogs/")
    else:
        return redirect("/login/")


def login(request):
    return render_to_response("login.html")


@psa("social:complete")
def auth(request, backend):
    socialToken = request.REQUEST.get("access_token")
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
            "dogs": dogs,
        },
        context_instance=RequestContext(request)
    )


def edit(request, dogId):
    dog = models.Dog.objects.get(id=dogId)
    return render_to_response(
        "editDog.html",
        context={
            "dog": dog,
            "dogForm": forms.DogForm(instance=dog),
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
        },
        context_instance=RequestContext(request)
    )


def base(request):
    return render_to_response(
        "_layout.html",
        context={
        }
    )


def loginBlock(request):
    return render_to_response(
        "loginBlock.html",
        context={
        }
    )


def news(request):
    return render_to_response(
        "news.html",
        context={

        },
        context_instance=RequestContext(request)
    )


def dog(request, dogId):
    dog = models.Dog.objects.get(id=dogId)

    return render_to_response(
        "dog.html",
        context={
            "dog": dog,
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
        },
        context_instance=RequestContext(request)
    )


def uploadPhoto(request):
    photo = models.Photo.objects.create(file=request.FILES["photoFile"])
    return JsonResponse({"url": photo.file.url})


@view_decorators.apiLoginRequired
def addDog(request):
    params = request.REQUEST
    birthDate = dateFromStr(params["birth_date"]) if "birth_date" in params else None
    dog = models.Dog.objects.create(
        nick=params["nick"],
        birthDate=birthDate,
        weight=params.get("weight", None),
        user=request.user,
        collarIdHash=hashlib.md5(params["collar_id"]).hexdigest() if "collar_id" in params else None
    )
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def editDog(request):
    params = request.REQUEST
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
            birthDate = dateFromStr(birthDate)
        else:
            birthDate = None
        dog.birthDate = birthDate
    if "weight" in params:
        weight = params["weight"]
        dog.weight = int(weight) if weight else None
    if request.FILES:
        dog.avatarFile = request.FILES["avatarFile"]
    if "collar_id" in params:
        collarId = params["collar_id"]
        dog.collarIdHash = hashlib.md5(collarId).hexdigest() if collarId else None
    dog.save()
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def getDog(request):
    params = request.REQUEST
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
    params = request.REQUEST
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })

    relatedDog = models.Dog.objects.get(id=params["related_id"])
    relation = models.DogRelation.objects.get_or_create(dog=dog, relatedDog=relatedDog)[0]
    relation.status = int(params["status"])
    relation.save()

    if relation.status == 1:
        nFriends = models.DogRelation(dog=dog, status=1).count()
        if nFriends == 1:
            models.Achievement.addAchievement(1, dog)

    if relation.status in [-1, 1]:
        comment = models.Comment(dog=dog, text="", type=3, relation=relation)
        dog.incEventCounter([comment])

    return JsonResponse(relation.toDict())


@view_decorators.apiLoginRequired
def subscribe(request):
    params = request.REQUEST
    dog = models.Dog.objects.get(id=params["id"])
    subscription = models.UserDogSubscription.objects.get_or_create(user=request.user, dog=dog)[0]
    return JsonResponse(subscription.toDict())


@view_decorators.apiLoginRequired
def unsubscribe(request):
    params = request.REQUEST
    dog = models.Dog.objects.get(id=params["id"])
    subscription = models.UserDogSubscription.objects.get(user=request.user, dog=dog)
    response = subscription.toDict()
    subscription.delete()
    return JsonResponse(response)


@view_decorators.apiLoginRequired
def addHome(request):
    params = request.REQUEST
    home = models.Home.objects.create(user=request.user, lat=Decimal(params["lat"]), lon=Decimal(params["lon"]))
    return JsonResponse(home.toDict())


def getDogStatus(dogId, dogIdToStatus):
    return dogIdToStatus.get(dogId, 2)


def addCloseDogEvents(dog, relatedDogs, added, relatedDogIdToStatus):
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
        params = request.REQUEST
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
            comment = models.Comment(dog=dog, text="", type=1, walk=walkInProgress)
            dog.incEventCounter([comment])
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

        relatedDogIdToStatus = {
            dogRelation.relatedDog_id: dogRelation.status
            for dogRelation in models.DogRelation.objects.filter(dog=dog,
                                                                 relatedDog__in=set(newCloseDogs + oldCloseDogs))
        }

        dogsAdded = set(newCloseDogs) - set(oldCloseDogs)
        dogsRemoved = set(oldCloseDogs) - set(newCloseDogs)
        for relatedDog in dogsAdded:
            models.CloseDogRelation.objects.create(dog=dog, relatedDog=relatedDog)
        addCloseDogEvents(dog, dogsAdded, True, relatedDogIdToStatus)
        models.CloseDogRelation.objects.filter(dog=dog, relatedDog__in=dogsRemoved).delete()
        addCloseDogEvents(dog, dogsRemoved, False, relatedDogIdToStatus)

        models.CloseDogEvent.removeOldEvents(dog.eventCounter)

        closeDogsStatus = [relatedDogIdToStatus[dog.id] for dog in newCloseDogs]
        return JsonResponse({
            "friends": closeDogsStatus.count(1),
            "enemies": closeDogsStatus.count(-1),
            "unknown": closeDogsStatus.count(2),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)})


@view_decorators.apiLoginRequired
def addTextComment(request):
    params = request.REQUEST
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    comment = models.Comment(dog=dog, text=params["text"], type=0)
    dog.incEventCounter([comment])
    return JsonResponse(comment.toDict())


@view_decorators.apiLoginRequired
def addPhotoComment(request):
    params = request.REQUEST
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    comment = models.Comment(dog=dog, text=params["text"], photo=params["photo"], type=2)
    dog.incEventCounter([comment])
    return JsonResponse(comment.toDict())


@view_decorators.apiLoginRequired
def deleteComment(request):
    params = request.REQUEST
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
    params = request.REQUEST
    like = models.Like(comment_id=params["comment_id"], user=request.user)[0]
    dog.incEventCounter([like])
    return JsonResponse(like.toDict())


@view_decorators.apiLoginRequired
def unlike(request):
    params = request.REQUEST
    like = models.Like.objects.get(comment_id=params["comment_id"], user=request.user)
    response = like.toDict()
    like.delete()
    return JsonResponse(response)


def fillResponseWithField(fields, fieldName, model, dogField, dog, eventCounter, response):
    if fieldName in fields:
        xargs = {
            dogField: dog
        }
        objects = model.objects.filter(
            eventCounter__range=[
                (eventCounter if eventCounter else 0) + 1,
                dog.eventCounter
            ],
            **xargs
        ).order_by("eventCounter")
        response[fieldName] = [
            obj.toDict() for obj in objects
        ]
    return response


@view_decorators.apiLoginRequired
def getDogEvents(request):
    params = request.REQUEST
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
                                                                 eventCounter__range=[
                                                                     eventCounter + 1,
                                                                     dog.eventCounter
                                                                 ]).order_by("eventCounter")
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
    response = fillResponseWithField(fields, "comments", models.Comment, "dog", dog, eventCounter, response)
    response = fillResponseWithField(fields, "likes", models.Like, "comment__dog", dog, eventCounter, response)
    response = fillResponseWithField(fields, "achievements", models.Achievement, "dog", dog, eventCounter, response)

    return JsonResponse(response)
