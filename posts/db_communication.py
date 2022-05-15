from time import time
from typing import List, TypedDict
from posts.models import Posts, Media, UserLikes
from users.db_communication import get_user



import base64

from django.core.files.base import ContentFile

from users.models import Users


def add_post(nickname: str, description: str, medias: List['TypedDict']):
    post = Posts(
        nickname=nickname,
        user_id=get_user(nickname=nickname).id,
        description=description,
        count_of_likes=0,
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
            post_id = post,
            media=data,
            media_type=media_type
        )
        media.save()
    return post.id
    

def like_post(user_id, post_id):
    print(UserLikes.objects.values())
    liked = UserLikes.objects.filter(user=Users.objects.get(id=user_id),
                                     post=Posts.objects.get(id=post_id)).first()
    if liked:
        liked.delete()
    else:
        new_like = UserLikes(user=Users.objects.get(id=user_id), post=Posts.objects.get(id=post_id))
        new_like.save()
    return not liked


def get_post_by_id(post_id):
    return Posts.objects.get(id=post_id)