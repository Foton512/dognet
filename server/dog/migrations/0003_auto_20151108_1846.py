# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dog.util


class Migration(migrations.Migration):

    dependencies = [
        ('dog', '0002_auto_20151105_1402'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='photo',
        ),
        migrations.AddField(
            model_name='comment',
            name='photoFile',
            field=models.FileField(null=True, upload_to=dog.util.getUniquePhotoPath),
        ),
        migrations.AddField(
            model_name='dog',
            name='breed',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dog',
            name='totalWalkLength',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='walk',
            name='length',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='dog',
            name='weight',
            field=models.FloatField(null=True),
        ),
    ]
