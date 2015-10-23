# -*- coding: utf-8 -*-
from django import forms


class PhotoForm(forms.Form):
    photoFile = forms.FileField(label="Выберите фото", help_text="test")