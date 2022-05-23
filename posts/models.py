from django.db import models


class Posts(models.Model):
    nickname = models.CharField(max_length=100, blank=True, null=True)
    user_id = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    timestamp = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'posts'


class Media(models.Model):
    post_id = models.ForeignKey('posts.Posts', models.DO_NOTHING, blank=True, null=True)
    media = models.FileField(null=True, blank=True, upload_to="media/")
    media_type = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'media'


class UserLikes(models.Model):
    post = models.ForeignKey('posts.Posts', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('users.Users', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userlikes'