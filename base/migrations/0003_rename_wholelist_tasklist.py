# Generated by Django 4.0.6 on 2022-07-18 21:11

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0002_rename_tasklist_task'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WholeList',
            new_name='TaskList',
        ),
    ]
