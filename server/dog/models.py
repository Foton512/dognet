from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    token = models.CharField(max_length=32)
    user = models.ForeignKey(User)


class Dog(models.Model):
    nick = models.CharField(max_length=100)
    birthDate = models.DateField(null=True)
    weight = models.IntegerField(null=True)

    def toDict(self):
        return {
            "id": self.id,
            "nick": self.nick,
            "birth_date": self.birthDate.strftime("%Y%m%d"),
            "weight": self.weight,
        }
