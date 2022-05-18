from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import posts.db_communication as db
from posts.models import Posts, Media, UserLikes
from users.db_communication import get_user
import json
from loguru import logger


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
        post = db.get_post_by_id(post_id)
        media = list(map(lambda x: {"media_type": x.media_type, "media": x.media.url}, list(Media.objects.filter(post_id=post_id).all())))
        like_set = list(map(lambda x: x.user_id, UserLikes.objects.filter(post=post_id).all()))
        print(like_set)
        return JsonResponse(
            {
                "post_id": post.id,
                "user_id": post.user_id,
                "user_name": post.nickname,
                "media_url": media,
                "count_of_likes": len(like_set),
                "timestamp": post.timestamp,
                "liked": like_set[1:]
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
