import os
import uuid
import datetime
from social.storage.django_orm import DjangoUserMixin


def getUniquePhotoPath(instance, filename):
    return os.path.join("photos", "{}.{}".format(uuid.uuid4(), filename.split(".")[-1]))


def datetimeToTimestmap(dt):
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


def getSocialUrlByUser(user):
    socialUser = DjangoUserMixin.get_social_auth_for_user(user)[0]
    if socialUser.provider == "vk-oauth2":
        return "vk.com/id{}".format(socialUser.uid)
        # TODO: Add facebook


