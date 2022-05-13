from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import users.db_communication as db
import json
import jwt
from time import time
import random
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
        url = f'https://gateway.api.sc/get/'\
            f'?user={SMS_API_LOGIN}'\
            f'&pwd={SMS_API_PASSWORD}'\
            f'&name_deliver=Ystories'\
            f'&text={code}'\
            f'&dadr={values["phone_number"]}'\
            f'&sadr={SMS_API_SADR}'
        r = requests.post(url)
        logger.info(f'SMS sent. ID: {r.text}')
        db.update_code(values['nickname'], code)
        db.update_phone_number(values['nickname'], values['phone_number'])
        return JsonResponse({
            'success': True
        })
    except:
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


# @csrf_exempt
# def login(request: HttpRequest):
#     return JsonResponse({'status': db.get_user(login) and db.get_user(json.load(request.body)["login"]).password == hashlib.sha256(json.load(request.body)["password"].encode("utf-8")).hexdigest()})