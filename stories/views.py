from django.shortcuts import render

# Create your views here.
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import stories.db_communication as db
import json
from stories.models import *
from loguru import logger

from users.db_communication import get_user


# body: {
#   "media": base64string,
#   "media_type": string
# }
# return: {
#   "success": bool
def add_stories(request: HttpRequest):
    try:
        values = json.loads(request.body)
        stories = values['media']
        type_ = values['media_type']
        token = request.headers.get('Authorization')
        db.add_new_stories(token, stories, type_)
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
def get_user_stories(request: HttpRequest, nickname: str):
    try:
        user = get_user(nickname=nickname)
        stories = sorted(db.get_stories(nickname=nickname), key=lambda x: x.timestamp)
        all_stories = []
        not_viewed_stories = []
        for i in stories:
            story = {
                "media": i.media.url,
                "media_type": i.media_type,
                "timestamp": i.timestamp,
            }
            all_stories.append(story)
            if user not in db.get_story_view(story_id=i.id):
                not_viewed_stories.append(story)
        photo = user.photo.url if user.photo else None
        return JsonResponse(
            {
                "nickname": nickname,
                "photo": photo,
                "all_stories": all_stories,
                "not_viewed_stories": not_viewed_stories
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)


# {"media": base64string, "success": bool, "timestamp": int}
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

