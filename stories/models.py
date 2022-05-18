from django.db import models

# Create your models here.


class Stories(models.Model):
    nickname = models.CharField(max_length=100, blank=True, null=True)
    media = models.FileField(null=True, blank=True, upload_to="stories/")
    media_type = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'stories'


class UserLikesStories(models.Model):
    liked_story = models.ForeignKey('stories.Stories', models.DO_NOTHING, blank=True, null=True)
    liked_user = models.ForeignKey('users.Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userlikesstories'


class UserViewStories(models.Model):
    viewed_story = models.ForeignKey('stories.Stories', models.DO_NOTHING, blank=True, null=True)
    viewed_user = models.ForeignKey('users.Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userviewsstories'