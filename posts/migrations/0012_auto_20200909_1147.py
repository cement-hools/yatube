# Generated by Django 2.2.6 on 2020-09-09 08:47

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0011_auto_20200909_1142'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('user', 'author')},
        ),
    ]
