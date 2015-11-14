# -*- coding: utf-8 -*-
import uuid
import hashlib
import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django.template import loader, Context
from social.apps.django_app.utils import psa
from django.utils import timezone
import geopy
from geopy.distance import distance
from geopy.point import Point

from dog import models, models_settings, forms
import view_decorators
from date_util import dateToStr, dateFromStr
import settings


def main(request):
    user = request.user
    if user.is_authenticated():
        if "currentDogId" in request.session:
            return redirect("/dog/{}/".format(request.session["currentDogId"]))
        else:
            try:
                lastDog = models.Dog.objects.filter(user=user).latest("id")
                return redirect("/dog/{}/".format(lastDog.id))
            except models.Dog.DoesNotExist:
                return render_to_response(
                    "blank.html",
                    context_instance=RequestContext(request)
                )
    else:
        return render_to_response(
            "blank.html",
            context_instance=RequestContext(request)
        )


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


def edit(request, dogId):
    dog = models.Dog.objects.get(id=dogId)
    ownDogs = models.Dog.objects.filter(user=request.user)
    return render_to_response(
        "editDog.html",
        context={
            "dog": dog,
            "ownDogs": ownDogs,
            "dogForm": forms.DogForm(instance=dog, initial={"breed": "Сиба Ину"}),
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
            "eventCounter": models.State.getState().eventCounter,
        },
        context_instance=RequestContext(request)
    )


def add(request):
    dogId = request.session.get("currentDogId", None)
    dog = models.Dog.objects.get(id=dogId) if dogId else None
    return render_to_response(
        "addDog.html",
        context={
            "dog": dog,
            "eventCounter": models.State.getState().eventCounter,
            "dogForm": forms.DogForm(
                initial={
                    "breed": "Сиба Ину",
                    "nick": "Конь",
                    "birthDate": "1990-10-23",
                    "weight": 42,
                    "collar_id": 1,
                }
            ),
        },
        context_instance=RequestContext(request)
    )

def maps(request):
    params = request.REQUEST
    dogId = request.session.get("currentDogId", None)
    dog = models.Dog.objects.get(id=dogId) if dogId else None
    ownDogs = models.Dog.objects.filter(user=request.user)

    filter = params.get("filter", "home")

    return render_to_response(
        "map.html",
        context={
            "dog": dog,
            "ownDogs": ownDogs,
            "filter": filter,
            "eventCounter": models.State.getState().eventCounter,
        },
        context_instance=RequestContext(request)
    )


def friends(request):
    params = request.REQUEST
    dogId = request.session.get("currentDogId", None)
    dog = models.Dog.objects.get(id=dogId) if dogId else None
    ownDogs = models.Dog.objects.filter(user=request.user)

    filter = params.get("filter", "all")
    if filter == "new":
        relatedDogs = [dogRelation.relatedDog for dogRelation in models.DogRelation.objects.filter(dog=dog)]
        relations = models.DogRelation.objects.filter(~Q(dog__in=relatedDogs), relatedDog=dog, status__in=[-1, 1])
        for relation in relations:
            relation.dog.onWalk = models.Walk.objects.filter(dog=relation.dog, inProgress=True).exists()
    else:
        if filter == "friends":
            status = [1]
        elif filter == "enemies":
            status = [-1]
        else:
            status = [-1, 1]
        relations = models.DogRelation.objects.filter(dog=dog, status__in=status)
        for relation in relations:
            relation.relatedDog.onWalk = models.Walk.objects.filter(dog=relation.relatedDog, inProgress=True).exists()
        if filter == "walk":
            relations = [relation for relation in relations if relation.relatedDog.onWalk]

    return render_to_response(
        "friends.html",
        context={
            "dog": dog,
            "ownDogs": ownDogs,
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
            "relations": relations,
            "filter": filter,
            "eventCounter": models.State.getState().eventCounter,
        },
        context_instance=RequestContext(request)
    )


def achievements(request):
    user = request.user
    dogId = request.session.get("currentDogId", None)
    dog = models.Dog.objects.get(id=dogId) if dogId else None
    ownDogs = models.Dog.objects.filter(user=user)

    achievementNumbers = [achievement.type for achievement in models.Achievement.objects.filter(dog=dog)]

    return render_to_response(
        "achievements.html",
        context={
            "dog": dog,
            "ownDogs": ownDogs,
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
            "achievements": {
                num: num in achievementNumbers for num in xrange(1, 5)
            },
            "eventCounter": models.State.getState().eventCounter,
        },
        context_instance=RequestContext(request)
    )


def news(request):
    user = request.user
    dogId = request.session.get("currentDogId", None)
    dog = models.Dog.objects.get(id=dogId) if dogId else None
    ownDogs = models.Dog.objects.filter(user=user)

    dogsWithComments = list(set(list(ownDogs) + [
        dogRelation.relatedDog for dogRelation in models.DogRelation.objects.filter(dog=dog, status__in=[-1, 1])
    ]))
    comments = models.Comment.objects.filter(dog__in=dogsWithComments).prefetch_related("comment_set").order_by("-eventCounter")

    return render_to_response(
        "news.html",
        context={
            "dog": dog,
            "ownDogs": ownDogs,
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
            "comments": comments,
            "eventCounter": models.State.getState().eventCounter,
        },
        context_instance=RequestContext(request)
    )


def dog(request, dogId):
    dog = models.Dog.objects.get(id=dogId)
    if dog.user == request.user:
        request.session["currentDogId"] = dogId
    ownDogs = models.Dog.objects.filter(user=request.user)
    comments = models.Comment.objects.filter(dog=dog).prefetch_related("comment_set").order_by("-eventCounter")

    return render_to_response(
        "dog.html",
        context={
            "dog": dog,
            "ownDogs": ownDogs,
            "birthDate": dateToStr(dog.birthDate) if dog.birthDate else "",
            "comments": comments,
            "ownDog": dog.user == request.user,
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
        breed=params["breed"] if "breed" in params else None,
        birthDate=birthDate,
        weight=params.get("weight", None),
        user=request.user,
        collarIdHash=hashlib.md5(params["collar_id"]).hexdigest() if "collar_id" in params else None,
        avatarFile=request.FILES["avatarFile"] if request.FILES else None
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
    if "breed" in params:
        dog.breed = params["breed"]
    if "birth_date" in params:
        birthDate = params["birth_date"]
        if birthDate:
            birthDate = dateFromStr(birthDate)
        else:
            birthDate = None
        dog.birthDate = birthDate
    if "weight" in params:
        weight = params["weight"]
        dog.weight = float(weight) if weight else None
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

    if relation.status in [-1, 1]:
        comment = models.Comment(dog=dog, text="", type=3, relation=relation)
        models.State.getState().incEventCounter([comment])

        if relation.status == 1:
            nFriends = models.DogRelation.objects.filter(dog=dog, status=1).count()
            if nFriends == 1:
                models.Achievement.addAchievement(1, dog)

        if relation.status == -1:
            nEnemies = models.DogRelation.objects.filter(dog=dog, status=-1).count()
            if nEnemies == 1:
                models.Achievement.addAchievement(2, dog)


    return JsonResponse(relation.toDict())


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
        models.State.getState().incEventCounter([closeDogEvent])


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

        deviceTime = datetime.datetime.fromtimestamp(int(params["timestamp"])).replace(tzinfo=None)

        createNewWalkPoint = False
        if walkInProgress is None:
            walkInProgress = models.Walk.objects.create(dog=dog, inProgress=True, lastTime=time)
            createNewWalkPoint = True
            nearestHome = dog.getNearestHome()
            if nearestHome:
                dog.createWalkPoint(walkInProgress, time, deviceTime, nearestHome.lat, nearestHome.lon)
        else:
            walkInProgress.lastTime = time
            walkInProgress.save()
            lastWalkPoint = models.WalkPoint.objects.filter(walk=walkInProgress).latest("eventCounter")
            distanceFromLast = distance(
                Point(float(lastWalkPoint.lat), float(lastWalkPoint.lon)),
                Point(float(lat), float(lon))
            ).meters
            if distanceFromLast >= models_settings.pointsDistanceThreshold:
                createNewWalkPoint = True
                walkInProgress.length += distanceFromLast
                prevTotalWalkLength = dog.totalWalkLength
                dog.totalWalkLength += distanceFromLast
                walkInProgress.save()
                dog.save()
                if prevTotalWalkLength < 50 and dog.totalWalkLength >= 50:
                    models.Achievement.addAchievement(3, dog)

        if createNewWalkPoint:
            dog.createWalkPoint(walkInProgress, time, deviceTime, lat, lon)

        approxDistanceThreshold = geopy.units.degrees(arcminutes=geopy.units.nautical(miles=1))
        closeCandidates = models.Dog.objects.filter(
            ~Q(user=dog.user),
            lat__range=(float(lat) - approxDistanceThreshold, float(lat) + approxDistanceThreshold),
            lon__range=(float(lon) - approxDistanceThreshold, float(lon) + approxDistanceThreshold)
        )
        newCloseDogs = [
            closeCandidate for closeCandidate in closeCandidates if distance(
                Point(lat, lon),
                Point(closeCandidate.lat, closeCandidate.lon)
            ).meters <= models_settings.pointsDistanceThreshold
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

        models.CloseDogEvent.removeOldEvents(models.State.getState().eventCounter)

        closeDogsStatus = [relatedDogIdToStatus[dog.id] for dog in newCloseDogs]

        if float(lat) == settings.testLat and float(lon) == settings.testLon:
            return JsonResponse({
                "friends": 1,
                "enemies": 0,
                "unknown": 0,
            })
        elif float(lat) == -settings.testLat and float(lon) == -settings.testLon:
            return JsonResponse({
                "friends": 0,
                "enemies": 1,
                "unknown": 0,
            })

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
    comment = models.Comment(
        dog=dog,
        text=params["text"],
        type=0,
        parentComment_id=params["parent_comment_id"] if "parent_comment_id" in params else None
    )
    models.State.getState().incEventCounter([comment])
    return JsonResponse(comment.toDict())


@view_decorators.apiLoginRequired
def addPhotoComment(request):
    params = request.REQUEST
    dog = models.Dog.objects.get(id=params["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    comment = models.Comment(dog=dog, text=params["text"], type=2)
    models.State.getState().incEventCounter([comment])
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
    models.State.getState().incEventCounter([like])
    return JsonResponse(like.toDict())


@view_decorators.apiLoginRequired
def unlike(request):
    params = request.REQUEST
    like = models.Like.objects.get(comment_id=params["comment_id"], user=request.user)
    response = like.toDict()
    like.delete()
    return JsonResponse(response)


def fillResponseWithField(fields, fieldName, model, dogField, dog, eventCounter, currentEventCounter, response):
    if fieldName in fields:
        xargs = {
            dogField: dog
        }
        objects = model.objects.filter(
            eventCounter__range=[
                (eventCounter if eventCounter else 0) + 1,
                currentEventCounter
            ],
            **xargs
        ).order_by("eventCounter")
        response[fieldName] = [
            obj.toDict() for obj in objects
        ]
    return response


@view_decorators.apiLoginRequired
def getDogEvents(request):
    currentEventCounter = models.State.getState().eventCounter
    params = request.REQUEST
    eventCounter = int(params["event_counter"]) if "event_counter" in params else None
    fields = params["fields"].split(",")
    try:
        dog = models.Dog.objects.get(id=params["id"])
    except:
        return JsonResponse({
            "lat": None,
            "lon": None,
            "walk": None,
            "close_dog_events": [],
            "comments": [],
            "replies": [],
            "achievements": [],
            "likes": [],
        })
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    user = request.user
    response = {
        "dog_id": dog.id,
        "event_counter": currentEventCounter,
    }

    walkInProgress = dog.checkFinishedWalks()

    if "lat" in fields:
        response["lat"] = float(dog.lat) if dog.lat else None
    if "lon" in fields:
        response["lon"] = float(dog.lon) if dog.lon else None
    if "walk" in fields:
        response["walk"] = {
            "id": walkInProgress.id,
            "path": walkInProgress.getPathWithinPeriod(eventCounter, currentEventCounter),
        } if walkInProgress else None
    if "close_dogs_events" in fields:
        if eventCounter:
            closeDogEvents = models.CloseDogEvent.objects.filter(dog=dog,
                                                                 eventCounter__range=[
                                                                     eventCounter + 1,
                                                                     currentEventCounter
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
    if "comments" in fields or "replies" in fields:
            ownDogs = models.Dog.objects.filter(user=user)
            dogsWithComments = list(set(list(ownDogs) + [
                dogRelation.relatedDog for dogRelation in models.DogRelation.objects.filter(dog=dog, status__in=[-1, 1])
            ]))
            comments = models.Comment.objects.filter(
                dog__in=dogsWithComments,
            )
            if eventCounter:
                comments = comments.filter(
                    eventCounter__range=[
                        eventCounter + 1,
                        currentEventCounter
                    ]
                )
            comments = comments.order_by("-eventCounter")
            replies = comments.filter(~Q(dog=dog), Q(parentComment__isnull=False))
            commentTemplate = loader.get_template('comment.html')
            if "comments" in fields:
                response["comments"] = [
                    {
                        "avatar": comment.dog.avatarFile.url if comment.dog.avatarFile else None,
                        "id": comment.id,
                        "parent_comment_id": comment.parentComment.id if comment.parentComment else None,
                        "html": commentTemplate.render(Context({"comment": comment}))
                    } for comment in comments
                ]
            if "replies" in fields:
                response["replies"] = [
                    {
                        "avatar": comment.dog.avatarFile.url if comment.dog.avatarFile else None,
                        "id": comment.id,
                        "parent_comment_id": comment.parentComment.id if comment.parentComment else None,
                        "html": commentTemplate.render(Context({"comment": comment}))
                    } for comment in replies
                ]

    if "achievements" in fields:
        achievements = models.Achievement.objects.filter(
            dog=dog,
            eventCounter__range=[
                (eventCounter if eventCounter else 0) + 1,
                currentEventCounter
            ],
        ).order_by("eventCounter")
        achievementTemplate = loader.get_template("achievement.html")
        for achievement in achievements:
            achievement.description = achievement.getDescription()
        response["achievements"] = [
            {
                "html": achievementTemplate.render(Context({"achievement": achievement}))
            } for achievement in achievements
        ]

    response = fillResponseWithField(fields, "likes", models.Like, "comment__dog", dog, eventCounter, currentEventCounter, response)

    return JsonResponse(response)
