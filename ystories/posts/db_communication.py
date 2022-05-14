import datetime

from posts.models import Posts
from users.db_communication import get_user


def add_post(nickname, media):
    post = Posts(
        nickname=nickname,
        user_id=get_user(nickname=nickname).id,
        count_of_likes=0,
        date=datetime.datetime.now(),
        #  liked=[]
    )
    for t, i in enumerate(media):
        post.media_url[t] = i
    post.save()
    return post.id


def like_post(nickname, post_id):
    post = get_post_by_id(post_id)
    post.liked.append(nickname)
    post.count_of_likes += 1
    post.save()


def get_post_by_id(post_id):
    return Posts.objects.get(id=post_id)
