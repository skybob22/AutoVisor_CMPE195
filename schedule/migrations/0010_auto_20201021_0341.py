# Generated by Django 3.1.2 on 2020-10-21 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_auto_20201021_0333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gearea',
            name='area',
            field=models.CharField(choices=[('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'), ('C1', 'C1'), ('C2', 'C2'), ('D1', 'D1'), ('D2', 'D2'), ('D3', 'D3'), ('E', 'E'), ('R', 'R'), ('S', 'S'), ('V', 'V'), ('Z', 'Z'), ('US1', 'US1'), ('US2', 'US2'), ('US3', 'US3')], max_length=3, unique=True),
        ),
    ]
