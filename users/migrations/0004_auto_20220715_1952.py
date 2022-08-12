# Generated by Django 3.2.6 on 2022-07-15 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_users_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscriptions',
            name='user_subscriber',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to='users.users'),
        ),
        migrations.AlterField(
            model_name='usersubscriptions',
            name='user_subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='users.users'),
        ),
    ]