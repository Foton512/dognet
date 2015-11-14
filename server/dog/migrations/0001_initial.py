# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import dog.util


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveSmallIntegerField()),
                ('eventCounter', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CloseDogEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.BooleanField()),
                ('status', models.SmallIntegerField(default=0)),
                ('eventCounter', models.PositiveIntegerField(default=0, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='CloseDogRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('type', models.PositiveSmallIntegerField()),
                ('photoFile', models.FileField(null=True, upload_to=dog.util.getUniquePhotoPath)),
                ('eventCounter', models.PositiveIntegerField(default=0, db_index=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('achievement', models.ForeignKey(to='dog.Achievement', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nick', models.CharField(max_length=100)),
                ('breed', models.CharField(max_length=100, null=True)),
                ('birthDate', models.DateField(null=True)),
                ('weight', models.FloatField(null=True)),
                ('avatarFile', models.FileField(null=True, upload_to=dog.util.getUniquePhotoPath)),
                ('collarIdHash', models.CharField(max_length=32, null=True)),
                ('lat', models.DecimalField(null=True, max_digits=9, decimal_places=6)),
                ('lon', models.DecimalField(null=True, max_digits=9, decimal_places=6)),
                ('totalWalkLength', models.FloatField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DogRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0)),
                ('dog', models.ForeignKey(related_name='+', to='dog.Dog')),
                ('relatedDog', models.ForeignKey(related_name='+', to='dog.Dog')),
            ],
        ),
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.DecimalField(max_digits=9, decimal_places=6)),
                ('lon', models.DecimalField(max_digits=9, decimal_places=6)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eventCounter', models.PositiveIntegerField(default=0, db_index=True)),
                ('comment', models.ForeignKey(to='dog.Comment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eventCounter', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=32)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserDogSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dog', models.ForeignKey(to='dog.Dog')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Walk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inProgress', models.BooleanField()),
                ('lastTime', models.DateTimeField()),
                ('length', models.FloatField(default=0)),
                ('dog', models.ForeignKey(to='dog.Dog')),
            ],
        ),
        migrations.CreateModel(
            name='WalkPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(db_index=True)),
                ('deviceTime', models.DateTimeField(db_index=True)),
                ('lat', models.DecimalField(max_digits=9, decimal_places=6)),
                ('lon', models.DecimalField(max_digits=9, decimal_places=6)),
                ('eventCounter', models.PositiveIntegerField(default=0, db_index=True)),
                ('walk', models.ForeignKey(to='dog.Walk')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='dog',
            field=models.ForeignKey(to='dog.Dog'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parentComment',
            field=models.ForeignKey(to='dog.Comment', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='relation',
            field=models.ForeignKey(to='dog.DogRelation', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='walk',
            field=models.ForeignKey(to='dog.Walk', null=True),
        ),
        migrations.AddField(
            model_name='closedogrelation',
            name='dog',
            field=models.ForeignKey(related_name='+', to='dog.Dog'),
        ),
        migrations.AddField(
            model_name='closedogrelation',
            name='relatedDog',
            field=models.ForeignKey(related_name='+', to='dog.Dog'),
        ),
        migrations.AddField(
            model_name='closedogevent',
            name='dog',
            field=models.ForeignKey(related_name='+', to='dog.Dog'),
        ),
        migrations.AddField(
            model_name='closedogevent',
            name='relatedDog',
            field=models.ForeignKey(related_name='+', to='dog.Dog'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='dog',
            field=models.ForeignKey(to='dog.Dog'),
        ),
        migrations.AlterIndexTogether(
            name='walk',
            index_together=set([('dog', 'inProgress')]),
        ),
    ]
