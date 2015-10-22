from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from dog import models
from datetime import datetime
from social.apps.django_app.utils import psa
import uuid
import view_decorators


def main(request):
    user = request.user
    if user.is_authenticated():
        return render_to_response(
            "main.html",
            context={
                "user": user,
            }
        )
    else:
        return redirect("login/")


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


def dog(request, dogId):
    dog = models.Dog.objects.get(id=dogId)

    return render_to_response(
        "dog.html",
        context={
            "nick": dog.nick,
            "birthDate": dog.birthDate.strftime("%Y%m%d"),
            "weight": dog.weight,
        },
    )


@view_decorators.apiLoginRequired
def addDog(request):
    fields = request.GET
    birthDate = datetime.strptime(fields["birth_date"], "%Y%m%d") if "birth_date" in fields else None
    dog = models.Dog.objects.create(
        nick=fields["nick"],
        birthDate=birthDate,
        weight=fields.get("weight", None),
        user=request.user
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
    dog.save()
    return JsonResponse(dog.toDict())


@view_decorators.apiLoginRequired
def getDog(request):
    fields = request.GET
    dog = models.Dog.objects.get(id=fields["id"])
    return JsonResponse(dog.toDict())
