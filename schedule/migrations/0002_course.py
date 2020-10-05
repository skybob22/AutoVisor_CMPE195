# Generated by Django 3.0.8 on 2020-10-05 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('department', models.TextField()),
                ('courseID', models.TextField()),
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'unique_together': {('department', 'courseID')},
            },
        ),
    ]
