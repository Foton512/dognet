from django.db import models

# Create your models here.

class Dog(models.Model):
    nick = models.CharField(max_length=100)
    birthDate = models.DateField()
    weight = models.IntegerField()
