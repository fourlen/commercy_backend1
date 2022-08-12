from django.shortcuts import render
from rest_framework.decorators import api_view

# Create your views here.
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import stories.db_communication as db
import json
from stories.models import *
from loguru import logger
from users.models import Users

# body: {
#   "media": base64string,
#   "media_type": string
# }
# return: {
#   "success": bool
@api_view(['POST'])
@csrf_exempt
def add_stories(request: HttpRequest):
    try:
        values = json.loads(request.body)
        stories = values['media']
        type_ = values['media_type']
        is_reversed = values['is_reversed']
        token = request.headers.get('Authorization')
        db.add_new_stories(token, stories, type_, is_reversed)
        return JsonResponse(
            {
                "success": True
            }
        )
    except Exception as ex:
        logger.error(ex)
        return JsonResponse(
            {
                "success": False,
                "error": str(ex)
            }
        )


# return: {
# "nickname": string,
# "photo": base64string,
# "all_stories": [
# {"media": base64string, "media_type": string, "timestamp": int}
# ...
# ]
# "not_viewed_stories": [
# {"media": base64string, "media_type": string, "timestamp": int}
# ...
# ]
@api_view(['GET'])
@csrf_exempt
def get_user_stories(request: HttpRequest, nickname: str):
    try:
        token = request.headers.get('Authorization')
        user = Users.objects.get(token=token)
        return JsonResponse(
            {
                db.feed_stories(nickname, user)
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


# {"media": base64string, "success": bool, "timestamp": int}
@api_view(['PUT'])
@csrf_exempt
def check_story(request: HttpRequest, story_id: int):
    story = db.get_target_story(story_id=story_id)
    try:
        db.set_story_view(story_id, token = request.headers.get('Authorization'))
        return JsonResponse(
            {
                "success": True,
                "media": story.media.url,
                "media_type": story.media_type,
                "timestamp": story.timestamp
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


# {"success": bool, "is_like_stayed": bool}
@api_view(['PUT'])
@csrf_exempt
def like_unlike_story(request: HttpRequest, story_id: int):
    try:
        token = request.headers.get('Authorization')
        status = db.set_unset_story_like(story_id, token)
        return JsonResponse(
            {
                "success": True,
                "is_like_stayed": status
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


@api_view(['DELETE'])
@csrf_exempt
def delete_stories(request: HttpRequest, story_id: int):
    try:
        token = request.headers.get('Authorization')
        story = Stories.objects.get(id=story_id)
        print(Stories.objects.filter(nickname=Users.objects.get(token=token).nickname))
        if story.nickname != Users.objects.get(token=token).nickname:
            return JsonResponse(
                {
                    "success": False,
                    "reason": "Not your story"
                }
            )
        for i in UserLikesStories.objects.filter(liked_story=story):
            i.delete()
        for i in UserViewStories.objects.filter(viewed_story=story):
            i.delete()
        story.delete()
        return JsonResponse(
            {
                "success": True
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)
