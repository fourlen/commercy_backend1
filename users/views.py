from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
import users.db_communication as db
import json
import jwt
from time import time
import random

from posts.models import UserLikes, Posts
from stories.models import UserLikesStories, Stories
from users.models import Users, UserSubscriptions, CodePhones
from ystories.settings import SECRET_KEY
import requests
from loguru import logger
import hashlib
from posts.db_communication import get_post_by_id
from rest_framework.decorators import api_view


# request
# {}
# response
# {
#     "token": string
# }

#@api_view(['POST'])
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

@api_view(['POST'])
@csrf_exempt
def check_phone_number(request: HttpRequest):
    try:
        values = json.loads(request.body)
        code = str(random.randint(0, 9999)).ljust(4, '0')
        db.update_phone_number(values['nickname'], values['phone_number'])
        body = json.dumps(
            {
                "messages": [
                    {
                        "phone": values['phone_number'],
                        "sender": "SMS DUCKOHT",
                        "clientId": "1",
                        "text": code
                    }
                ],
                "statusQueueName": "myQueue",
                "showBillingDetails": True,
                "login": "z1597935568350",
                "password": "528374"
            }
        )
        r = requests.post('https://api.iqsms.ru/messages/v2/send.json', data=body)
        logger.info(f'SMS sent. Response: {r.text}')
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

@api_view(['POST'])
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

@api_view(['POST'])
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
    if not values['password']:
        user.delete()
        return HttpResponse()
    password = hashlib.sha256(values['password'].encode("utf-8")).hexdigest()
    db.update_password(
        token=token,
        password=password
    )
    return JsonResponse(
        {
            'user_created': True,
	    'id': user.id,
        }
    )

@api_view(['POST'])
@csrf_exempt
def login(request: HttpRequest):
    values = json.loads(request.body)
    nickname = values["nickname"]
    password = hashlib.sha256(values["password"].encode("utf-8")).hexdigest()
    user = db.get_user(nickname=nickname)
    if not user:
        user = db.get_user(phone_number=nickname)
        if not user:
            user = db.get_user(email=nickname)
            if not user:
                return JsonResponse(
                    {
                        'is_correct': False,
                    }
                )
    if user.is_banned:
        return HttpResponseNotAllowed("Banned")
    is_correct = bool(user and user.password == password)
    if is_correct:
        return JsonResponse(
            {
                'is_correct': is_correct,
                'token': user.token,
                'nickname': user.nickname,
        'id': user.id,
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

@api_view(['POST'])
@csrf_exempt
def edit_profile(request: HttpRequest):
    print(Users.objects.get(id=68).token)
    try:
        values = json.loads(request.body)
        token = request.headers.get('Authorization')
        nickname = values["nickname"]
        if db.get_user(nickname=nickname) and db.get_user(nickname=nickname).token != token:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Nickname is already exist"
                }
            )
        db.update_description(token, Users.objects.get(token=token).nickname, values["full_name"], 
                              values["nickname"], values["description"],
                              values["gender"], values["birthday"], values["photo"], values["email"])
        return JsonResponse(
            {
                "success": True,
                "user": db.get_full_user(token, nickname)
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)

@api_view(['POST'])
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

@api_view(['GET'])
@csrf_exempt
def get_user(request: HttpRequest, nickname: str, typ: str):
    try:
        token = request.headers.get('Authorization')
        json_ = db.get_full_user(token, nickname, typ)
        return JsonResponse(json_)
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)

@api_view(['POST'])
@csrf_exempt
def search(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        values = json.loads(request.body)
        try:
            i = values["i"]
        except:
            i = 0
        string = values["string"]
        return JsonResponse(
            {
                "all_users": db.get_result_by_search(string, token, i)
            }
        )
    except Exception as ex:
        logger.error(ex)
        return HttpResponseBadRequest(ex)

@api_view(['GET'])
@csrf_exempt
def get_notifications(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        user = db.get_user(token=token)
        all_likes_stories = UserLikesStories.objects.all()
        all_user_stories = Stories.objects.filter(nickname=user.nickname)
        list1 = list(map(lambda x: {"type": "likes_stories",
                                    "story_url": x.liked_story.media.url,
                                    "media_type": x.liked_story.media_type,
                                    "user_liked_nickname": x.liked_user.nickname,
                                    "is_in_your_subscriptions": db.is_your_subscriber(x.liked_user, token),
                                    "user_liked_photo": x.liked_user.photo.url
                                    if x.liked_user.photo else None,
                                    "timestamp": x.timestamp},
                         filter(lambda x: x.liked_story in all_user_stories and x.liked_user != db.get_user(token=token),
                                all_likes_stories)))
        all_my_subs = UserSubscriptions.objects.filter(user_subscription=Users.objects.get(
                             token=token))
        list2 = list(map(lambda x: {"type": "subscriptions",
                                    "sub_nickname": x.user_subscriber.nickname,
                                    "is_in_your_subscriptions": db.is_your_subscriber(x.user_subscriber, token),
                                    "sub_photo": x.user_subscriber.photo.url
                                    if x.user_subscriber.photo else None,
                                    "timestamp": x.timestamp},
                         filter(lambda x: x.timestamp, all_my_subs)))
        all_likes_posts = UserLikes.objects.all()
        all_user_posts = Posts.objects.filter(nickname=Users.objects.get(
            token=token).nickname)
        list3 = list(map(lambda x: {"type": "likes_posts",
                                    "post": get_post_by_id(x.post_id),
                                    "user_liked_nickname": x.user.nickname,
                                    "is_in_your_subscriptions": db.is_your_subscriber(x.user, token),
                                    "user_liked_photo": x.user.photo.url
                                    if x.user.photo else None,
                                    "timestamp": x.timestamp},
                         filter(lambda x: x.post in all_user_posts and x.user != db.get_user(token=token),
                                all_likes_posts)))
        list_ = sorted(list1 + list2 + list3, key=lambda x: x["timestamp"])[::-1]
        const = 86400
        return JsonResponse(
            {
                "sorted_notif_day": list(filter(lambda x: time() - x["timestamp"] < const, list_)),
                "sorted_notif_week": list(filter(lambda x: const < time() - x["timestamp"] < const * 7, list_)),
                "sorted_notif_month": list(filter(lambda x: const * 7 < time() - x["timestamp"] < const * 31, list_)),
            }
        )
    except Exception as ex:
        return HttpResponseBadRequest(ex)

@api_view(['POST'])
@csrf_exempt
def discard_step_1(request: HttpRequest):
    try:
        values = json.loads(request.body)
        code = str(random.randint(0, 9999)).ljust(4, '0')
        db.create_code_discard(values['phone_number'], code)
        body = json.dumps(
            {
                "messages": [
                    {
                        "phone": values['phone_number'],
                        "sender": "SMS DUCKOHT",
                        "clientId": "1",
                        "text": code
                    }
                ],
                "statusQueueName": "myQueue",
                "showBillingDetails": True,
                "login": "pkvr0101509",
                "password": "778835"
            }
        )
        r = requests.post('https://api.iqsms.ru/messages/v2/send.json', data=body)
        logger.info(f'SMS sent. Response: {r.text}')
        return JsonResponse({
            'success': True
        })
    except Exception as ex:
        return  HttpResponseBadRequest(ex)

@api_view(['POST'])
@csrf_exempt
def discard_step_2(request: HttpRequest):
    values = json.loads(request.body)
    phone_number = values["phone_number"]
    code = values["code"]
    codephone = CodePhones.objects.filter(phone_number=phone_number, sms_code=code).first()
    if codephone:
        codephone.delete()
        return JsonResponse({
            'is_correct': True,
            'all_profiles': list(map(lambda x: {"nickname": x.nickname,
                                     "id": x.id, "token": x.token, "photo": x.photo.url if x.photo else None}, 
                                     Users.objects.filter(phone_number=phone_number)))
        })
    else:
        return JsonResponse({
            'is_correct': False
        })

@api_view(['POST'])
@csrf_exempt
def discard_step_3(request: HttpRequest):
    values = json.loads(request.body)
    token = Users.objects.get(id=values["id"]).token
    password = hashlib.sha256(values['password'].encode("utf-8")).hexdigest()
    db.update_password(token, password)
    return JsonResponse({
            'success': True,
            'token': token
        })

@api_view(['POST'])
@csrf_exempt
def chat_search(request: HttpRequest):
    try:
        values = json.loads(request.body)
        token = request.headers.get('Authorization')
        return JsonResponse(
            db.chat_search(values["str"], token)
        )
    except Exception as ex:
        return HttpResponseBadRequest(ex)


@api_view(['GET'])
@csrf_exempt
def get_notification_state(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        user = db.get_user(token=token)
        return JsonResponse(
            {
                "state": user.is_view_notification
            }
        )
    except Exception as ex:
        return HttpResponseBadRequest(ex)


@api_view(['PUT'])
@csrf_exempt
def set_notification_state(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        user = db.get_user(token=token)
        user.is_view_notification = True
        user.save()
        return JsonResponse(
            {
                "state": user.is_view_notification,
                "success": True
            }
        )
    except Exception as ex:
        return HttpResponseBadRequest(ex)


@api_view(['PUT'])
@csrf_exempt
def change_photo(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        user = db.get_user(token=token)
        values = json.loads(request.body)
        photo = db.change_photo(user, values["photo"])
        return JsonResponse(
            {
                "photo": photo.url if photo else None
            }
        )
    except Exception as ex:
        return HttpResponseBadRequest(ex)

