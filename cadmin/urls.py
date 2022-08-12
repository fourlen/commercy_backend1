from django.urls import path
from . import views


urlpatterns = [
    path('auth', views.auth),
    path('add_admin', views.add_admin),
    path('get_all_admins', views.get_all_admins),
    path('get_all_users', views.get_all_users),
    path('delete_user', views.delete_user),
    path('get_all_posts', views.get_all_posts),
    path('ban_user', views.ban_user),
    path('unban_user', views.unban_user),
    path('update_post', views.update_post),
    path('delete_post', views.delete_post),
    path('get_all_stories', views.get_all_stories),
    path('delete_stories', views.delete_stories),
]