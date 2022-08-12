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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view

import os
from django.views.static import serve


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER_WEB_APP = os.path.join(BASE_DIR, 'adminka')

schema_view = get_swagger_view(title='Pastebin API')

def flutter_redirect(request, resource):
        return serve(request, resource, FLUTTER_WEB_APP)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('stories/', include('stories.urls')),
    path('cadmin/', include('cadmin.urls')),
    path('adminka/', lambda r: flutter_redirect(r, 'index.html')),
    path('adminka', lambda r: flutter_redirect(r, 'index.html')),
    path('adminka/<path:resource>', flutter_redirect),
    url(r'^$', schema_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
