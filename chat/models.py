from django.db import models


class Message(models.Model):
    from_user = models.ForeignKey('users.Users', on_delete=models.CASCADE)
    to_user = models.ForeignKey('users.Users', on_delete=models.CASCADE)
    message = models.CharField(max_length=2000)

    class Meta:
        managed = True
        db_table = 'message'