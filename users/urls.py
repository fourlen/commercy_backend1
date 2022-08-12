"""ystories URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('check_nickname/<slug:nickname>', views.check_nickname),
    path('check_phone_number', views.check_phone_number),
    path('check_code', views.check_code),
    path('set_password', views.set_password),
    path('login', views.login),
    path('edit_profile', views.edit_profile),
    path('get_user_by_<slug:typ>/<slug:nickname>', views.get_user),
    path('subscribe/<slug:nickname>', views.subscribe_unsubscribe),
    path('search', views.search),
    path('notification', views.get_notifications),
    path('discard_step_1', views.discard_step_1),
    path('discard_step_2', views.discard_step_2),
    path('discard_step_3', views.discard_step_3),
    path('chat_search', views.chat_search),
    path('get_notif_state', views.get_notification_state),
    path('set_notif_state', views.set_notification_state),
    path('change_photo', views.change_photo)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
