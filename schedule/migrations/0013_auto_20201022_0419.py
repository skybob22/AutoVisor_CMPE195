# Generated by Django 3.1.2 on 2020-10-22 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0012_auto_20201022_0408'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='catalog',
            new_name='catalogue',
        ),
    ]