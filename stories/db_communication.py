import base64
from time import time

from django.core.files.base import ContentFile

import users.db_communication as db
from users.models import Users
from stories.models import *


def add_new_stories(token: str, data: str, data_type: str, is_reversed):
    user = Users.objects.get(token=token)
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    stories = Stories(nickname=user.nickname, media=None, timestamp=time(), media_type=data_type)
    stories.save()
    data = ContentFile(base64.b64decode(imgstr), name=f'{user.nickname}_stories_{stories.id}.{ext}')
    stories.media = data
    stories.is_reversed = is_reversed
    stories.save()


def get_stories(nickname: str):
    return list(filter(lambda x: time() - x.timestamp <= 86400, Stories.objects.filter(nickname=nickname).all()))

def get_target_story(story_id: int):
    return Stories.objects.filter(id=story_id).first()


def set_unset_story_like(story_id: int, token: str):
    user = db.get_user(token=token)
    story = get_target_story(story_id)
    owner = db.get_user(nickname=story.nickname)
    like = UserLikesStories.objects.filter(liked_user=user, liked_story=story).first()
    if like:
        like.delete()
    else:
        new_like = UserLikesStories(liked_user=user, liked_story=story, timestamp=time())
        owner.is_view_notification = False
        owner.save()
        new_like.save()
    return like


def get_story_likes(story_id: int):
    story = get_target_story(story_id)
    return list(map(lambda x: x.liked_user, list(UserLikesStories.objects.filter(liked_story=story))))


def set_story_view(story_id: int, token: str):
    user = db.get_user(token=token)
    story = get_target_story(story_id)
    view = UserViewStories.objects.filter(viewed_user=user, viewed_story=story).first()
    if not view:
        new_view = UserViewStories(viewed_user=user, viewed_story=story)
        new_view.save()


def get_story_view(story_id: int):
    story = get_target_story(story_id)
    return list(map(lambda x: x.viewed_user, list(UserViewStories.objects.filter(viewed_story=story))))


def feed_stories(nickname, main_user):
    user = db.get_user(nickname=nickname)
    stories = sorted(get_stories(nickname=nickname), key=lambda x: x.timestamp)
    all_stories = []
    flag = True
    index_ = 0
    for i in stories:
        id_ = i.id
        story = {
            "id": id_,
            "media": i.media.url,
            "media_type": i.media_type,
            "timestamp": i.timestamp,
        }
        all_stories.append(story)
        if main_user not in get_story_view(story_id=id_) and flag:
            flag = False
            index_ = stories.index(i)
    photo = user.photo.url if user.photo else None
    return {
            "nickname": nickname,
            "photo": photo,
            "all_stories": all_stories,
            "index": index_,
            "is_full_viewed": flag
        }

def get_user_stories_count(nickname: str) -> int:
    return len(Stories.objects.filter(nickname=nickname).all())


def get_all_stories():
    return [{
        'stories_id': story.id,
        'nickname': story.nickname,
        'media': story.media.url,
        'media_type': story.media_type,
        'is_reversed': story.is_reversed,
        'timestamp': story.timestamp
    }
    for story in Stories.objects.filter().all()]


def delete_stories(stories_id):
    story = Stories.objects.get(id=stories_id)
    for i in UserLikesStories.objects.filter(liked_story=story):
        i.delete()
    for i in UserViewStories.objects.filter(viewed_story=story):
        i.delete()
    story.delete()