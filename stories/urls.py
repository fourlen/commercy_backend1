from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('add_stories', views.add_stories),
    path('<slug:nickname>/get_stories', views.get_user_stories),
    path('story<int:story_id>', views.check_story),
    path('like_story<int:story_id>', views.like_unlike_story),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
