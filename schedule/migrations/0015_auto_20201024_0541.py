# Generated by Django 3.1.2 on 2020-10-24 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0014_auto_20201024_0517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preferredcourse',
            name='reqID',
        ),
        migrations.AddField(
            model_name='preferredcourse',
            name='reqID',
            field=models.ManyToManyField(blank=True, default=None, to='schedule.GERequirement'),
        ),
    ]