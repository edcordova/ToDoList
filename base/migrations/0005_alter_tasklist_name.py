# Generated by Django 4.0.6 on 2022-07-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_tasklist_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasklist',
            name='name',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
