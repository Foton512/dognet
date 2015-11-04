# -*- coding: utf-8 -*-
from django import forms
import models


class PhotoForm(forms.Form):
    photoFile = forms.FileField(label="Выберите фото", help_text="test")


class DogForm(forms.ModelForm):
    nick = forms.CharField(label="Nick", max_length=100)
    weight = forms.DecimalField(label="Weight", max_value=100, min_value=0)

    class Meta:
        model = models.Dog
        fields = ["nick", "weight"]
