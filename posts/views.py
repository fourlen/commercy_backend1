from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import posts.db_communication as db
from posts.models import Posts
from users.db_communication import get_user
import json
import jwt
from time import time
import random

from users.models import Users
from ystories.settings import SMS_API_LOGIN, SMS_API_PASSWORD, SMS_API_SADR, SECRET_KEY
import requests
from loguru import logger
import hashlib


@csrf_exempt
def create_post(request: HttpRequest):
    values = json.loads(request.body)
    nickname = values['nickname']
    medias = values['media']
    description = values['description']
    token = request.headers.get('Authorization')
    if token != get_user(nickname=nickname).token:
        return HttpResponseBadRequest('Unauthorized')
    post_id = db.add_post(
        nickname=nickname,
        description=description,
        medias=medias
    )
    return JsonResponse(
        {
            "post_created": True,
            "id": post_id
        }
    )
    try:
        values = json.loads(request.body)
        nickname = values['nickname']
        media = values['media']
        description = values['description']
        token = request.headers.get('Authorization')
        if token != get_user(nickname=nickname).token:
            return HttpResponseBadRequest('Unauthorized')
        post_id = db.add_post(
            nickname=nickname,
            description=description,
            media=media
        )
        return JsonResponse(
            {
                "post_created": True,
                "id": post_id
            }
        )
    except:
        return JsonResponse(
            {
                "post_created": False
            }
        )


@csrf_exempt
def get_post(request: HttpRequest, id: int):
    try:
        post = db.get_post_by_id(id)
        return JsonResponse(
            {
                "post_id": post.id,
                "user_id": post.user_id,
                "user_name": post.nickname,
                #  "media_url": post.media_url,
                "count_of_likes": post.count_of_likes,
                "date": post.date,
                #  "liked": post.liked,
            }
        )
    except Exception as ex:
        print(ex)
        return JsonResponse(
            {
                "try_to_get_post": False,
            }
        )