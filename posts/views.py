from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import posts.db_communication as db
from posts.models import Posts, Media, UserLikes
from users.db_communication import get_user, get_subscriptions
import json
from loguru import logger
from stories.models import Stories
from users.models import Users
import stories
from rest_framework.decorators import api_view
from time import time


@api_view(['POST'])
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
                "post": db.get_post_by_id(post_id),
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


@api_view(['GET'])
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


@api_view(['PUT'])
@csrf_exempt
def like_unlike_post(request: HttpRequest, post_id: int):
    try:
        token = request.headers.get('Authorization')
        state = db.like_post(user_id=get_user(token=token).id, post_id=post_id)
        logger.info("success: true")
        return JsonResponse(
            {
                "post": db.get_post_by_id(post_id),
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


@api_view(['GET'])
@csrf_exempt
def get_feed(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user(token=token)
    all_subs_id = list(map(lambda x: x.id, get_subscriptions(user.nickname)))
    all_posts = list(filter(lambda x: x['user_id'] in all_subs_id or x['user_id'] == user.id,
                            list(Posts.objects.values())[::-1]))
    json_ret = []
    all_stories = list(filter(lambda x: Users.objects.get(nickname=x.nickname)
                                   in get_subscriptions(user.nickname),
                         list(filter(lambda x: time() - x.timestamp <= 86400, Stories.objects.all()))))
    all_stories_json = (list(map(lambda x: {"nickname": x.nickname,
                                            "avatar": Users.objects.get(nickname=x.nickname).photo.url if
                                            Users.objects.get(nickname=x.nickname).photo else None,
                                            "stories": stories.db_communication.feed_stories(x.nickname, user)},
                                 all_stories)))
    copy = []
    for i in all_stories_json:
        if i not in copy:
            copy.append(i)
    k = 0
    for i in all_posts:
        k += 1
        if k > 14:
            break
        json_ret.append(db.get_post_by_id(i['id']))
    return JsonResponse(
        {
            "feed": json_ret,
            "stories_users": copy
        }
    )


@api_view(['POST'])
@csrf_exempt
def get_rec(request: HttpRequest):
    try:
        values = json.loads(request.body)
        i = values["i"] if "i" in values else None
        rec = sorted(list(Posts.objects.values()), key=(lambda x: db.get_post_by_id(x['id'])['count_of_likes']))
        posts = list(map(lambda x: db.get_post_by_id(x['id']), rec))
        return JsonResponse(
            {
                'posts': posts[20 * i: 20 * (i + 1)] if i else posts
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


@api_view(['DELETE'])
@csrf_exempt
def delete_post(request: HttpRequest, post_id: int):
    try:
        token = request.headers.get('Authorization')
        post = Posts.objects.get(id=post_id)
        if post.nickname != Users.objects.get(token=token).nickname:
            return JsonResponse(
                {
                    "success": False,
                    "reason": "Not your post"
                }
            )
        for i in UserLikes.objects.filter(post=post):
            i.delete()
        for i in Media.objects.filter(post_id=post.id):
            i.delete()
        post.delete()
        return JsonResponse(
            {
                "success": True
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)
