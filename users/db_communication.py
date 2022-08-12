from time import time

from posts.db_communication import get_user_posts
from posts.models import Posts, UserLikes, Media
from stories.db_communication import get_story_view, get_stories, feed_stories, get_user_stories_count
from stories.models import Stories, UserLikesStories, UserViewStories
from stories.views import get_user_stories
from .models import Users, UserSubscriptions, CodePhones
from django.core.files.base import ContentFile
import base64

def create_code_discard(phone, code):
    phone = CodePhones(phone_number=phone, sms_code=code)
    phone.save()


def is_nickname_exists(nickname: str) -> bool:
    user = Users.objects.filter(
        nickname=nickname
    ).first()
    if user is None:
        return False
    if user.password is None:
        return False
    if time() - user.registration_timestamp > 15 * 60 and not user.is_phone_confirmed:
        user.delete()
        return False
    return True

def add_user(nickname: str, token: str, password: str = '',
             phone_number: str = None, email: str = None, is_admin=False):
    user = Users(
        nickname=nickname,
        password=password,
        token=token,
        phone_number=phone_number,
        email=email,
        is_admin=is_admin,
        registration_timestamp=time()
    )
    user.save()

def get_all_users():
    return [
        {
            'nickname': user.nickname,
            'user_id': user.id,
            'phone': user.phone_number,
            'email': user.email,
            'birth': user.timestamp,
            'gender': user.gender,
            'posts_count': get_user_posts_count(user.id),
            'stories_count': get_user_stories_count(user.nickname),
            'likes_count': get_user_likes_count(user.id)
        }
    for user in Users.objects.filter().all()]


def delete_user(user_id: int):
    user = Users.objects.filter(id=user_id).first()
    if not user:
        return False
    for stories in Stories.objects.filter(nickname=user.nickname).all():
        stories.delete()
    user.delete()
    return True
def get_user(**kwargs) -> Users:
    return Users.objects.filter(
        **kwargs
    ).first()


def update_phone_number(nickname, phone):
    user = Users.objects.get(nickname=nickname)
    user.phone_number = phone
    user.save()


def update_code(nickname, code):
    user = Users.objects.get(nickname=nickname)
    user.sms_code = code
    user.save()


def update_phone_status(nickname, phone_status):
    user = Users.objects.get(nickname=nickname)
    user.is_phone_confirmed = phone_status
    user.save()


def update_password(token, password):
    user = Users.objects.get(token=token)
    user.password = password
    user.save()


def update_description(token, old_nickname, full_name=None, nickname=None, description=None, gender=None, birthday=None,
                       photo: str = None, mail: str = None):
    user = Users.objects.get(token=token)
    user.full_name = full_name
    if nickname:
        for i in Stories.objects.filter(nickname=old_nickname):
            i.nickname = nickname
            i.save()
        for i in Posts.objects.filter(nickname=old_nickname):
            i.nickname = nickname
            i.save()
        user.nickname = nickname
    user.nickname = nickname
    user.description = description
    user.gender = gender
    user.timestamp = birthday
    data = photo
    if photo and photo != "photo":
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{user.nickname}_ava.{ext}')
    if photo != "photo":
        user.photo = data
    user.email = mail
    user.save()


def subscribe_unsubscribe(token, nickname):
    user_subscription = get_user(nickname=nickname)
    relation = UserSubscriptions.objects.filter(user_subscriber=get_user(token=token),
                                                user_subscription=user_subscription).first()
    if relation:
        relation.delete()
    else:
        sub = UserSubscriptions(user_subscriber=get_user(token=token), user_subscription=get_user(nickname=nickname),
                                timestamp=time())
        user_subscription.is_view_notification = False
        user_subscription.save()
        sub.save()
    return not relation


def get_subscribers(nickname):
    return list(map(lambda x: x.user_subscriber,
                    list(UserSubscriptions.objects.filter(user_subscription=get_user(nickname=nickname).id).all())))


def get_subscriptions(nickname):
    return list(map(lambda x: x.user_subscription,
                    UserSubscriptions.objects.filter(user_subscriber=get_user(nickname=nickname).id).all()))


def get_result_by_search(string, token, i):
    return list(filter(lambda x: string in x["nickname"],
                            map(lambda x: {
                                "nickname": x["nickname"],
                                "photo": x["photo"],
                                "is_in_your_subscription": is_you_subscriber(get_user(nickname=x["nickname"]), token),
                                "is_in_your_subscribers": is_your_subscriber(get_user(nickname=x["nickname"]), token),
                                "full_name": x["full_name"],
                            },
                                list(Users.objects.values()))))[20 * i: 20 * (i + 1)]
def is_your_subscriber(user, token):
    return user in get_subscribers(Users.objects.get(token=token).nickname)


def is_you_subscriber(user, token):
    return user in get_subscriptions(Users.objects.get(token=token).nickname)


def get_full_user(token, nickname, typ='str'):
    photo_url = None
    if typ == 'str':
        user = get_user(nickname=nickname)
    else:
        user = get_user(id=nickname)
    stories = sorted(get_stories(nickname=nickname), key=lambda x: x.timestamp)
    all_stories = []
    not_viewed_stories = []
    for i in stories:
        id_ = i.id
        story = {
            "id": id_,
            "media": i.media.url,
            "media_type": i.media_type,
            "timestamp": i.timestamp,
        }
        all_stories.append(story)
        if user not in get_story_view(story_id=i.id):
            not_viewed_stories.append(story)
    if user.photo:
        photo_url = user.photo.url
    json_ = {
        "id": user.id,
        "nickname": user.nickname,
        "phone_number": user.phone_number,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_phone_confirmed": user.is_phone_confirmed,
        "full_name": user.full_name,
        "description": user.description,
        "gender": user.gender,
        "birthday": user.timestamp,
	"is_banned": user.is_banned,
        "photo": photo_url,
        "posts": get_user_posts(user.nickname),
        "stories": {
            "all_stories": all_stories,
            "not_viewed_stories": not_viewed_stories,
            "stories": feed_stories(user.nickname, user)
        },
        "subscribers": list(map(lambda x: {"nickname": x.nickname, "photo": (x.photo.url if x.photo else None),
                                           "is_in_your_subscription": is_you_subscriber(x, user.token),
                                           "is_in_your_subscribers": is_your_subscriber(x, user.token)
                                           } if x else None,
                                get_subscribers(user.nickname))),
        "subscriptions": list(map(lambda x: {"nickname": x.nickname, "photo": (x.photo.url if x.photo else None),
                                             "is_in_your_subscription": is_you_subscriber(x, user.token),
                                             "is_in_your_subscribers": is_your_subscriber(x, user.token)
                                             } if x else None,
                                  get_subscriptions(user.nickname))),
        "is_in_your_subscription": is_you_subscriber(user, token),
        "is_in_your_subscribers": is_your_subscriber(user, token)
    }
    return json_


def chat_search(str_: str, token: str):
    all_users = list(filter(lambda x: str_ in x.nickname, Users.objects.all()))
    all_subs = list(filter(lambda x: str_ in x.nickname, get_subscribers(get_user(token=token).nickname)))
    return {
        "all_users": list(map(lambda x: {
            "id": x.id,
            "photo": x.photo.url if x.photo else None,
            "nickname": x.nickname,
            "name": x.full_name}, all_users)),
        "all_users_from_subscriptions": list(map(lambda x: {
            "id": x.id,
            "photo": x.photo.url if x.photo else None,
            "nickname": x.nickname,
            "name": x.full_name}, all_subs)),
    }


def get_user_posts_count(user_id: int) -> int:
    return len(Posts.objects.filter(user_id=user_id).all())


def get_user_likes_count(user_id: int) -> int:
    return len(UserLikes.objects.filter(user_id=user_id).all())


def get_all_users():
    return [
        {
            'nickname': user.nickname,
            'user_id': user.id,
            'phone': user.phone_number,
            'email': user.email,
            'birth': user.timestamp,
            'gender': user.gender,
            'posts_count': get_user_posts_count(user.id),
	    "is_banned": user.is_banned,
            'stories_count': get_user_stories_count(user.nickname),
            'likes_count': get_user_likes_count(user.id)
        }
    for user in Users.objects.filter().all()]


def delete_user(user_id: int):
    user = Users.objects.filter(id=user_id).first()
    if not user:
        return False
    for stories in Stories.objects.filter(nickname=user.nickname).all():
        stories.delete()
    for userLikesStories in UserLikesStories.objects.filter(liked_user_id=user.id).all():
        userLikesStories.delete()
    for userViewStories in UserViewStories.objects.filter(viewed_user_id=user.id).all():
        userViewStories.delete()
    for post in Posts.objects.filter(user_id=user.id).all():
        for media in Media.objects.filter(post_id_id=post.id).all():
            media.delete()
        for userLikes in UserLikes.objects.filter(post_id=post.id).all():
            userLikes.delete()
        post.delete()
    user.delete()
    return True


def change_is_banned(user_id: int):
    user = Users.objects.filter(id=user_id).first()
    if not user:
        return False
    user.is_banned = False if user.is_banned else True
    user.save()
    return True


def ban_user(user_id: int):
    user = Users.objects.filter(id=user_id).first()
    if not user:
        return False
    user.is_banned = True
    user.save()
    return True


def unban_user(user_id: int):
    user = Users.objects.filter(id=user_id).first()
    if not user:
        return False
    user.is_banned = False
    user.save()
    return True


def change_photo(user: Users, photo: str):
    if photo:
        format, imgstr = photo.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{user.nickname}_ava.{ext}')
        user.photo = data
    else:
        user.photo = None
    user.save()
    return user.photo
