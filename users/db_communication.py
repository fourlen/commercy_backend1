from time import time

import users
from posts.db_communication import get_user_posts
from stories.db_communication import get_story_view, get_stories
from .models import Users, UserSubscriptions
from django.core.files.base import ContentFile
import base64


def is_nickname_exists(nickname: str) -> bool:
    user = Users.objects.filter(
        nickname=nickname
    ).first()
    if user is None:
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
        is_admin=is_admin
    )
    user.save()


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


def update_description(token, full_name=None, nickname=None, description=None, gender=None, birthday=None,
                       photo: str = None):
    user = Users.objects.get(token=token)
    if full_name:
        user.full_name = full_name
    if nickname:
        user.nickname = nickname
    if description:
        user.description = description
    if gender:
        user.gender = gender
    if birthday:
        user.timestamp = birthday
    if photo:
        data = photo
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{user.nickname}_ava.{ext}')
        user.photo = data
    user.save()


def subscribe_unsubscribe(token, nickname):
    relation = UserSubscriptions.objects.filter(user_subscriber=get_user(token=token),
                                                user_subscription=get_user(nickname=nickname)).first()
    if relation:
        relation.delete()
    else:
        sub = UserSubscriptions(user_subscriber=get_user(token=token), user_subscription=get_user(nickname=nickname),
                                timestamp=time())
        sub.save()
    return not relation


def get_subscribers(nickname):
    return list(map(lambda x: x.user_subscriber,
                    list(UserSubscriptions.objects.filter(user_subscription=get_user(nickname=nickname).id).all())))


def get_subscriptions(nickname):
    return list(map(lambda x: x.user_subscription,
                    UserSubscriptions.objects.filter(user_subscriber=get_user(nickname=nickname).id).all()))


def get_result_by_search(string, token):
    return list(list(filter(lambda x: string in x["nickname"],
                            map(lambda x: {'nickname': x["nickname"], 'photo': x['photo'], "is_in_your_subscription":
                                is_you_subscriber(get_user(nickname=x["nickname"]), token),
                                           "is_in_your_subscribers": is_your_subscriber(get_user(nickname=x["nickname"])
                                                                                        , token)},
                                list(Users.objects.values())))))


def is_your_subscriber(user, token):
    return user in get_subscribers(Users.objects.get(token=token).nickname)


def is_you_subscriber(user, token):
    return user in get_subscriptions(Users.objects.get(token=token).nickname)


def get_full_user(token, nickname):
    photo_url = None
    user = get_user(nickname=nickname)
    stories = sorted(get_stories(nickname=nickname), key=lambda x: x.timestamp)
    all_stories = []
    not_viewed_stories = []
    for i in stories:
        story = {
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
        "nickname": user.nickname,
        "phone_number": user.phone_number,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_phone_confirmed": user.is_phone_confirmed,
        "full_name": user.full_name,
        "description": user.description,
        "gender": user.gender,
        "birthday": user.timestamp,
        "photo": photo_url,
        "posts": get_user_posts(user.nickname),
        "stories": {
            "all_stories": all_stories,
            "not_viewed_stories": not_viewed_stories
        },
        "subscribers": list(map(lambda x: {"nickname": x.nickname, "photo": (x.photo.url if x.photo else None),
                                           "is_in_your_subscription": is_you_subscriber(x, user.token),
                                           "is_in_your_subscribers": is_your_subscriber(x, user.token)
                                           },
                                get_subscribers(user.nickname))),
        "subscriptions": list(map(lambda x: {"nickname": x.nickname, "photo": (x.photo.url if x.photo else None),
                                             "is_in_your_subscription": is_you_subscriber(x, user.token),
                                             "is_in_your_subscribers": is_your_subscriber(x, user.token)
                                             },
                                  get_subscriptions(user.nickname))),
        "is_in_your_subscription": is_you_subscriber(user, token),
        "is_in_your_subscribers": is_your_subscriber(user, token)
    }
    return json_
