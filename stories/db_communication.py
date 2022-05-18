import base64
from time import time
from typing import TypedDict

from django.core.files.base import ContentFile

from users.db_communication import get_user
from users.models import Users
from stories.models import *


def add_new_stories(token: str, data: str, data_type: str):
    user = Users.objects.get(token=token)
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    stories = Stories(nickname=user.nickname, media=None, timestamp=time(), media_type=data_type)
    data = ContentFile(base64.b64decode(imgstr), name=f'{user.nickname}_{stories.id}.{ext}')
    stories.media = data
    stories.save()


def get_stories(nickname: str):
    return list(Stories.objects.filter(nickname=nickname).all())


def get_target_story(story_id: int):
    return Stories.objects.filter(id=story_id).first()


def set_unset_story_like(story_id: int, token: str):
    user = get_user(token=token)
    story = get_target_story(story_id)
    like = UserLikesStories.objects.filter(liked_user=user, liked_story=story).first()
    if like:
        like.delete()
    else:
        new_like = UserLikesStories(liked_user=user, liked_story=story)
        new_like.save()
    return like


def get_story_likes(story_id: int):
    story = get_target_story(story_id)
    return list(map(lambda x: x.liked_user, list(UserLikesStories.objects.filter(liked_story=story))))


def set_story_view(story_id: int, token: str):
    user = get_user(token=token)
    story = get_target_story(story_id)
    view = UserViewStories.objects.filter(viewed_user=user, viewed_story=story).first()
    if not view:
        new_view = UserViewStories(viewed_user=user, viewed_story=story)
        new_view.save()


def get_story_view(story_id: int):
    story = get_target_story(story_id)
    return list(map(lambda x: x.viewed_user, list(UserViewStories.objects.filter(viewed_story=story))))
