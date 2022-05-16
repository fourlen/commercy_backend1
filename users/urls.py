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
<<<<<<< HEAD
    path('edit_profile', views.edit_profile),
    path('get_user/<int:user_id>', views.get_user)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
    path('edit_profile', views.set_description),
    path('<slug:nickname>/subscribe', views.subscribe_unsubscribe),
]
>>>>>>> 84dc341d730d5e2be9f1f8f671c9bd6604c9776b
