# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import os
import uuid


class Token(models.Model):
    token = models.CharField(max_length=32)
    user = models.ForeignKey(User)


class Photo(models.Model):
    file = models.FileField(
        upload_to=lambda instance, filename: os.path.join(
            "photos", "{}.{}".format(uuid.uuid4(), filename.split(".")[-1])
        )
    )


class Dog(models.Model):
    nick = models.CharField(max_length=100)
    birthDate = models.DateField(null=True)
    weight = models.IntegerField(null=True)
    user = models.ForeignKey(User)
    avatar = models.CharField(max_length=1000, null=True)

    def toDict(self):
        return {
            "id": self.id,
            "nick": self.nick,
            "birth_date": self.birthDate.strftime("%Y%m%d") if self.birthDate else "",
            "weight": self.weight,
            "avatar": self.avatar,
        }
