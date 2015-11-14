# -*- coding: utf-8 -*-
from django import forms
import models
from django.forms.widgets import FileInput
import models_settings


class DogForm(forms.ModelForm):
    weight = forms.DecimalField(min_value=0, max_value=100)
    avatarFile = forms.FileField(widget=FileInput)
    collar_id = forms.CharField(max_length=10)
    breed = forms.ChoiceField(
        choices=[(breed, breed) for breed in models_settings.breeds] + [(None, "-")],
    )

    class Meta:
        model = models.Dog
        fields = ["avatarFile", "nick", "weight", "birthDate", "breed", "collar_id"]
