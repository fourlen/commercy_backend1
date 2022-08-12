from django.db import models


class CAdmin(models.Model):
    login = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=500, blank=True, null=True)
    token = models.CharField(max_length=500, blank=True, null=True, unique=True)

    class Meta:
        managed = True
        db_table = 'admin'
