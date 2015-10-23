# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from dog import models
from datetime import datetime
from social.apps.django_app.utils import psa
import uuid
import view_decorators
import forms


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
    fields = request.GET
    birthDate = datetime.strptime(fields["birth_date"], "%Y%m%d") if "birth_date" in fields else None
    dog = models.Dog.objects.create(
        nick=fields["nick"],
        birthDate=birthDate,
        weight=fields.get("weight", None),
        user=request.user,
        avatar=fields.get("avatar", None)
    )
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def editDog(request):
    fields = request.GET
    dog = models.Dog.objects.get(id=fields["id"])
    if dog.user != request.user:
        return JsonResponse({
            "error": "You don't have rights to execute this method",
        })
    if "nick" in fields:
        dog.nick = fields["nick"]
    if "birth_date" in fields:
        birthDate = fields["birth_date"]
        if birthDate:
            birthDate = datetime.strptime(birthDate, "%Y%m%d")
        else:
            birthDate = None
        dog.birthDate = birthDate
    if "weight" in fields:
        weight = fields["weight"]
        dog.weight = int(weight) if weight else None
    if "avatar" in fields:
        avatar = fields["avatar"]
        dog.avatar = avatar if avatar else None
    dog.save()
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def getDog(request):
    fields = request.GET
    dog = models.Dog.objects.get(id=fields["id"])
    return JsonResponse(dog.toDict())
