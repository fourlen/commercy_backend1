# Generated by Django 3.2.6 on 2022-05-12 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('password', models.CharField(blank=True, max_length=500, null=True)),
                ('token', models.CharField(blank=True, max_length=500, null=True)),
                ('is_admin', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'users',
                'managed': True,
            },
        ),
    ]