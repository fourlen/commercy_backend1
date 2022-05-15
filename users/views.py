from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import users.db_communication as db
import json
import jwt
from time import time
import random

from users.models import UserSubscriptions, Users
from ystories.settings import SMS_API_LOGIN, SMS_API_PASSWORD, SMS_API_SADR, SECRET_KEY
import requests
from loguru import logger
import hashlib


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
    print(request.body)
    values = json.loads(request.body)
    nickname = values["nickname"]
    password = hashlib.sha256(values["password"].encode("utf-8")).hexdigest()
    user = db.get_user(nickname=nickname)
    is_correct = user and user.password == password
    if is_correct:
        return JsonResponse(
            {
                'is_correct': is_correct,
                'token': user.token
            }
        )
    return JsonResponse(
        {
            'is_correct': is_correct,
        }
    )


@csrf_exempt
def set_description(request: HttpRequest):
    values = json.loads(request.body)
    token = request.headers.get('Authorization')
    try:
        db.update_description(token, values["full_name"], values["nickname"], values["description"],
                              values["gender"], values["birthday"], values["photo"])
        return JsonResponse(
            {
                "success": True,
            }
        )
    except ValidationError as ex:
        return JsonResponse(
            {
                "success": "invalid_date. It must be in YYYY-MM-DD format"
            }
        )


@csrf_exempt
def subscribe_unsubscribe(request: HttpRequest, user_id: int):
    token = request.headers.get('Authorization')
    try:
        answer = db.subscribe_unsubscribe(token, user_id)
        print(db.get_subscribers(user_id))
        print(db.get_subscriptions(Users.objects.get(token=token).id))
        return JsonResponse(
            {
                "success": True,
                "subscribe": answer
            }
        )
    except Exception as ex:
        logger.info(ex)
        return JsonResponse(
            {
                "success": False
            }
        )