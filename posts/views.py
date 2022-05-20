from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import posts.db_communication as db
from posts.models import Posts, Media, UserLikes
from users.db_communication import get_user, get_subscriptions
import json
from loguru import logger

from users.models import Users


@csrf_exempt
def create_post(request: HttpRequest):
    try:
        values = json.loads(request.body)
        medias = values['media']
        description = values['description']
        token = request.headers.get('Authorization')
        nickname = get_user(token=token).nickname
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
    except Exception as ex:
        logger.error(ex)
        return JsonResponse(
            {
                "post_created": False
            }
        )


@csrf_exempt
def get_post(request: HttpRequest, post_id: int):
    try:
        return JsonResponse(
            db.get_post_by_id(post_id=post_id)
        )
    except Exception as ex:
        logger.error(ex)
        return JsonResponse(
            {
                "success": False,
            }
        )


@csrf_exempt
def like_unlike_post(request: HttpRequest, post_id: int):
    try:
        token = request.headers.get('Authorization')
        state = db.like_post(user_id=get_user(token=token).id, post_id=post_id)
        logger.info("success: true")
        return JsonResponse(
            {
                "success": True,
                "is_like": state
            }
        )
    except Exception as ex:
        logger.error(ex)
        return JsonResponse(
            {
                "success": False,
            }
        )


@csrf_exempt
def get_feed(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        user = get_user(token=token)
        all_subs_id = list(map(lambda x: x.id, get_subscriptions(user.nickname)))
        all_posts = list(filter(lambda x: x['user_id'] in all_subs_id, list(Posts.objects.values())[::-1]))
        json_ret = []
        k = 0
        for i in all_posts:
            k += 1
            if k > 14:
                break
            json_ret.append(db.get_post_by_id(i['id']))
        return JsonResponse(
            {
                "feed": json_ret
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)
