from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import users.db_communication as db
import json
import jwt
from time import time
import random

from posts.models import UserLikes
from stories.models import UserLikesStories
from users.models import Users, UserSubscriptions
from ystories.settings import SMS_API_LOGIN, SMS_API_PASSWORD, SMS_API_SADR, SECRET_KEY
import requests
from stories.db_communication import get_stories, get_story_view
from loguru import logger
import hashlib
from posts.db_communication import get_user_posts


# request
# {}
# response
# {
#     "token": string
# }


@csrf_exempt
def check_nickname(request: HttpRequest, nickname: str):
    exists = db.is_nickname_exists(nickname)
    if not exists:
        token = jwt.encode({
            'nickname': nickname,
            'timestamp': str(time())
        }, key=SECRET_KEY)
        db.add_user(
            token=token,
            nickname=nickname
        )
        return JsonResponse(
            {
                'exists': exists,
                'token': token
            }
        )
    return JsonResponse(
        {
            'exists': exists
        }
    )


# request
# {
#     'nickname': ...,
#     'phone_number': ...
# }
# reponse
# {
#     "success": Bool
# }


@csrf_exempt
def check_phone_number(request: HttpRequest):
    try:
        values = json.loads(request.body)
        code = str(random.randint(0, 9999)).ljust(4, '0')
        db.update_phone_number(values['nickname'], values['phone_number'])
        url = f'https://gateway.api.sc/get/' \
              f'?user={SMS_API_LOGIN}' \
              f'&pwd={SMS_API_PASSWORD}' \
              f'&name_deliver=Ystories' \
              f'&text={code}' \
              f'&dadr={values["phone_number"]}' \
              f'&sadr={SMS_API_SADR}'
        r = requests.post(url)
        logger.info(f'SMS sent. ID: {r.text}')
        db.update_code(values['nickname'], code)
        return JsonResponse({
            'success': True
        })
    except Exception:
        return JsonResponse({
            'success': False
        })


# request
# {
#     'nickname': ...,
#     'code': ...
# }
# response
# {
#     "is_correct": Bool
# }


@csrf_exempt
def check_code(request: HttpRequest):
    values = json.loads(request.body)
    try:
        is_correct = db.get_user(nickname=values['nickname']).sms_code == values['code']
    except:
        return HttpResponseBadRequest("User not found")
    db.update_phone_status(values['nickname'], is_correct)
    return JsonResponse(
        {
            'is_correct': is_correct
        }
    )


# request
# {
#     "password": ...
# }
# response
# {
#     "user_created": Bool
# }


@csrf_exempt
def set_password(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = db.get_user(
        token=token
    )
    print(user.nickname)
    print(user.phone_number)
    if user is None:
        return HttpResponseBadRequest("Unauthorized user")
    elif not user.is_phone_confirmed:
        return HttpResponseBadRequest("Phone is not confirmed")
    elif user.password:
        return HttpResponseBadRequest("Password is already exists")
    values = json.loads(request.body)
    password = hashlib.sha256(values['password'].encode("utf-8")).hexdigest()
    db.update_password(
        token=token,
        password=password
    )
    return JsonResponse(
        {
            'user_created': True
        }
    )


@csrf_exempt
def login(request: HttpRequest):
    values = json.loads(request.body)
    nickname = values["nickname"]
    password = hashlib.sha256(values["password"].encode("utf-8")).hexdigest()
    user = db.get_user(nickname=nickname)
    is_correct = bool(user and user.password == password)
    if is_correct:
        return JsonResponse(
            {
                'is_correct': is_correct,
                'token': user.token,
                'nickname': user.nickname
            }
        )
    return JsonResponse(
        {
            'is_correct': is_correct,
        }
    )


# {
#     "full_name": string,
#     "nickname": string,
#     "description": string,
#     "gender": string, male/female
#     "birthday": "YYYY-MM-DD",
#     "photo": base64
# }


@csrf_exempt
def edit_profile(request: HttpRequest):
    values = json.loads(request.body)
    token = request.headers.get('Authorization')
    try:
        nickname = values["nickname"]
        if db.get_user(nickname=nickname) and db.get_user(nickname=nickname).token != token:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Nickname is already exist"
                }
            )
        db.update_description(token, values["full_name"], values["nickname"], values["description"],
                              values["gender"], values["birthday"], values["photo"])
        return JsonResponse(
            {
                "success": True,
                "user": db.get_full_user(token, nickname)
            }
        )
    except ValidationError as ex:
        logger.error(ex)
        return HttpResponseBadRequest("Incorrect fields")


@csrf_exempt
def subscribe_unsubscribe(request: HttpRequest, nickname: str):
    token = request.headers.get('Authorization')
    try:
        answer = db.subscribe_unsubscribe(token, nickname)
        logger.info(db.get_subscribers(nickname))
        logger.info(db.get_subscriptions(Users.objects.get(token=token).nickname))
        return JsonResponse(
            {
                "success": True,
                "subscribe": answer,
                "subscription_on": db.get_full_user(token, nickname)
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


@csrf_exempt
def get_user(request: HttpRequest, nickname: str):
    try:
        token = request.headers.get('Authorization')
        json_ = db.get_full_user(token, nickname)
        return JsonResponse(json_)
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


@csrf_exempt
def search(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        values = json.loads(request.body)
        string = values["string"]
        return JsonResponse(
            {
                "all_users": db.get_result_by_search(string, token)
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


@csrf_exempt
def get_notifications(request: HttpRequest):
    print(Users.objects.values())
    token = request.headers.get('Authorization')
    print(list(UserLikes.objects.filter(user=Users.objects.get(token=token)).all()))
    list_ = list(map(lambda x: dict(x), list(UserLikes.objects.filter(user=Users.objects.get(token=token)).all())))
    return JsonResponse(
        {
            "sorted_notif": list_
        }
    )
