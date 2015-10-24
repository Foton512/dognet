# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from dog import models
from social.apps.django_app.utils import psa
import uuid
import view_decorators
import forms
import hashlib
import datetime
from django.utils import timezone
from decimal import Decimal


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
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def getOwnDogs(request):
    dogs = models.Dog.objects.filter(user=request.user)
    return JsonResponse([dog.toDict() for dog in dogs], safe=False)


@view_decorators.apiLoginRequired
def setDogRelation(request):
    params = request.GET
    dog = models.Dog.objects.get(id=params["dog_id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    relatedDog = models.Dog.objects.get(id=params["related_dog_id"])
    relation = models.DogRelation.objects.get_or_create(dog=dog, relatedDog=relatedDog)[0]
    relation.status = int(params["status"])
    relation.save()
    return JsonResponse(relation.toDict())


@view_decorators.apiLoginRequired
def addHome(request):
    params = request.GET
    home = models.Home.objects.create(user=request.user, lat=Decimal(params["lat"]), lon=Decimal(params["lon"]))
    return JsonResponse(home.toDict())


def addWalkPoint(request):
    time = timezone.now()
    params = request.GET
    collarIdHash = params["collar_id_hash"]
    dog = models.Dog.objects.get(collarIdHash=collarIdHash)
    walkInProgress = dog.checkFinishedWalks()
    if walkInProgress is None:
        walkInProgress = models.Walk.objects.create(dog=dog, inProgress=True)
        # TODO: add first point in nearest house
    walkPoint = models.WalkPoint.objects.create(
        walk=walkInProgress,
        time=time,
        deviceTime=datetime.datetime.fromtimestamp(int(params["timestamp"])).replace(tzinfo=None),
        lat=Decimal(params["lat"]),
        lon=Decimal(params["lon"])
    )

    return JsonResponse(walkPoint.toDict())