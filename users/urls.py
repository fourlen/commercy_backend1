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
    path('get_user/<slug:nickname>', views.get_user),
    path('subscribe/<slug:nickname>', views.subscribe_unsubscribe),
    path('search', views.search),
    path('notification', views.get_notifications)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
