# Generated by Django 3.1.2 on 2020-10-21 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0007_auto_20201019_0828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gerequirement',
            name='numCourses',
        ),
        migrations.AddField(
            model_name='gerequirement',
            name='allowOverlap',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gerequirement',
            name='numUnits',
            field=models.IntegerField(default=3),
        ),
    ]
