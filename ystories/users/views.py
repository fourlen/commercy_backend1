from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
import users.db_communication as db
import json
import jwt
from time import time

@csrf_exempt
def check_nickname(request: HttpRequest, nickname: str):
    exists = db.is_nickname_exists(nickname)
    if exists:
        token = jwt.encode({
            'nickname': nickname,
            'timestamp': str(time())
        })
        db.add_user(
            token=token,
            nickname=nickname
        )
    return JsonResponse(
        {
            'exists': exists
        }
    )


# @csrf_exempt
# def create_user(request: HttpRequest):
#     values = json.loads(request.body)
#     try:
#         token = jwt.encode({
#             'nickname': values['nickname'],
#             'timestamp': str(time())
#         })

#     except:
#         return HttpResponseBadRequest('Invalid input')
