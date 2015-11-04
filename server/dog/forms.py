# -*- coding: utf-8 -*-
from django import forms
import models


class DogForm(forms.ModelForm):
    weight = forms.DecimalField(min_value=0, max_value=100)

    class Meta:
        model = models.Dog
        fields = ["avatarFile", "nick", "weight", "birthDate"]
