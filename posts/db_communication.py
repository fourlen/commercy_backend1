from time import time
from typing import List, TypedDict
from posts.models import Posts, Media, UserLikes
import users.db_communication as udb

import base64
from django.core.files.base import ContentFile

from users.models import Users


def add_post(nickname: str, description: str, medias: List['TypedDict']):
    post = Posts(
        nickname=nickname,
        user_id=udb.get_user(nickname=nickname).id,
        description=description,
        timestamp=time(),
    )
    post.save()
    for i, media in enumerate(medias):
        data = media['base64']
        media_type = media['media_type']
        format, imgstr = data.split(';base64,') 
        ext = format.split('/')[-1] 
        data = ContentFile(base64.b64decode(imgstr), name=f'{nickname}_{post.id}_{i}.{ext}')
        media = Media(
            post_id=post,
            media=data,
            media_type=media_type
        )
        media.save()
    return post.id
    

def like_post(user_id, post_id):
    liked = UserLikes.objects.filter(user=Users.objects.get(id=user_id),
                                     post=Posts.objects.get(id=post_id)).first()
    if liked:
        liked.delete()
    else:
        new_like = UserLikes(user=Users.objects.get(id=user_id), post=Posts.objects.get(id=post_id),
                             timestamp=time())
        new_like.save()
    return not liked


def get_post_by_id(post_id):
    post = Posts.objects.get(id=post_id)
    media = list(map(lambda x: {"media": x.media.url, "media_type": x.media_type}, list(Media.objects.filter(post_id=post_id).all())))
    like_set = list(map(lambda x: x.user_id, UserLikes.objects.filter(post=post_id).all()))
    return {
        "post_id": post.id,
        "user_id": post.user_id,
        "user_name": post.nickname,
        "media_url": media,
        "count_of_likes": len(like_set),
        "date": post.timestamp,
        "liked": like_set
    }


def get_user_posts(nickname: str):
    posts = list(Posts.objects.filter(nickname=nickname).all())
    posts_with_media = []
    for post in posts:
        posts_with_media.append(
            get_post_by_id(post_id=post.id)
        )
    return posts_with_media
