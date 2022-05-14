from django.db import models


class Posts(models.Model):
    nickname = models.CharField(max_length=100, blank=True, null=True)
    user_id = models.PositiveIntegerField(blank=True, null=True, max_length=100)
    media_url = [{"url": models.URLField(null=True, max_length=100),
                  "media_type": models.CharField(max_length=100, blank=True, null=True)} for i in range(10)]
    count_of_likes = models.PositiveIntegerField(blank=True, null=True, max_length=100)
    date = models.DateField(blank=True, null=True)
    #  liked = [models.CharField(max_length=100, blank=True, null=True, unique=True) ]

    class Meta:
        managed = True
        db_table = 'posts'
