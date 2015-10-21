from django.shortcuts import render_to_response
from dog import models


def main(request):
    return render_to_response("main.html")


def dog(request, dogId): 
    dog = models.Dog.objects.get(id=dogId)

    return render_to_response(
        "main.html",
        context={
            "nick": dog.nick,
            "birthDate": dog.birthDate.strftime("%Y%m%d"),
            "weight": dog.weight,
        },
    )
