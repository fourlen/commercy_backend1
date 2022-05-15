# Generated by Django 3.2.6 on 2022-05-15 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, max_length=100, null=True)),
                ('user_id', models.PositiveIntegerField(blank=True, null=True)),
                ('count_of_likes', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=2000, null=True)),
                ('timestamp', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'posts',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserLikes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='posts.posts')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='users.users')),
            ],
            options={
                'db_table': 'userlikes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(blank=True, null=True, upload_to='media/')),
                ('media_type', models.CharField(blank=True, max_length=100, null=True)),
                ('post_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='posts.posts')),
            ],
            options={
                'db_table': 'media',
                'managed': True,
            },
        ),
    ]