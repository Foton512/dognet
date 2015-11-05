# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import dog.util


class Migration(migrations.Migration):

    dependencies = [
        ('dog', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Photo',
        ),
        migrations.RemoveField(
            model_name='dog',
            name='avatar',
        ),
        migrations.AddField(
            model_name='comment',
            name='parentComment',
            field=models.ForeignKey(to='dog.Comment', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 5, 14, 2, 27, 474000), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dog',
            name='avatarFile',
            field=models.FileField(null=True, upload_to=dog.util.getUniquePhotoPath),
        ),
    ]
