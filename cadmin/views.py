from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponseNotAllowed, JsonResponse, HttpResponseServerError
import cadmin.db_communication as db
import users.db_communication as users_db
import posts.db_communication as posts_db
import stories.db_communication as stories_db
import json
import hashlib
from rest_framework.decorators import api_view

@api_view(['POST'])
@csrf_exempt
def auth(request: HttpRequest):
    try:
        values = json.loads(request.body)
        admin = db.get_admin(
            login=values['login']
        )
        if admin:
            if admin.password != hashlib.sha256(values['password'].encode("utf-8")).hexdigest():
                return JsonResponse({
                    'error': 'wrong password'
                })
            return JsonResponse({
                'token': admin.token
            })
        else:
            return JsonResponse({
                'error': 'User not found'
            })
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def add_admin(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        token = db.add_admin(
            values=values
        )
        return JsonResponse({
            'token': token
        })
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['GET'])
@csrf_exempt
def get_all_admins(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        return JsonResponse(
            db.get_all_admins(), safe=False
        )
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['GET'])
@csrf_exempt
def get_all_users(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        return JsonResponse(
            users_db.get_all_users(), safe=False
        )
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def delete_user(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        success = users_db.delete_user(values['user_id'])
        return JsonResponse({
            'success': success
        })
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def ban_user(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        success = users_db.ban_user(values['user_id'])
        return JsonResponse(
            {
                'success': success
            }
        )
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def unban_user(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        success = users_db.unban_user(values['user_id'])
        return JsonResponse(
            {
                'success': success
            }
        )
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['GET'])
@csrf_exempt
def get_all_posts(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        return JsonResponse(
            posts_db.get_all_posts(), safe=False
        )
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def update_post(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        posts_db.update_post(
            post_id=values['post_id'],
            new_description=values['new_description']
        )
        return JsonResponse({
            'success': True
        })
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def delete_post(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        posts_db.delete_post(values['post_id'])
        return JsonResponse({
            'success': True
        })
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')


@api_view(['GET'])
@csrf_exempt
def get_all_stories(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        return JsonResponse(
            stories_db.get_all_stories(), safe=False
        )
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')

@api_view(['POST'])
@csrf_exempt
def delete_stories(request: HttpRequest):
    try:
        token = request.headers.get('Authorization')
        admin = db.get_admin(
            token=token
        )
        if not admin:
            return HttpResponseNotAllowed("You are not an admin")
        values = json.loads(request.body)
        stories_db.delete_stories(values['stories_id'])
        return JsonResponse({
            'success': True
        })
    except Exception as err:
        return HttpResponseServerError(f'Something goes wrong: {err}')