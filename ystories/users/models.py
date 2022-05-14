from django.db import models


class Users(models.Model):
    nickname = models.CharField(max_length=100, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    password = models.CharField(max_length=500, blank=True, null=True)
    token = models.CharField(max_length=500, blank=True, null=True, unique=True)
    is_admin = models.BooleanField(blank=True, null=True)
    sms_code = models.CharField(max_length=4, blank=True, null=True)
    is_phone_confirmed = models.BooleanField(blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    gender = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="image/", blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'users'
