# Generated by Django 3.1.2 on 2020-11-16 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0025_auto_20201116_0635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogue',
            name='term',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Fall', 'Fall')], max_length=6),
        ),
        migrations.AlterField(
            model_name='semesterschedule',
            name='term',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Fall', 'Fall')], max_length=6),
        ),
        migrations.AlterField(
            model_name='student',
            name='currentTerm',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Fall', 'Fall')], default='Fall', max_length=6),
        ),
        migrations.AlterField(
            model_name='student',
            name='startTerm',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Fall', 'Fall')], default='Fall', max_length=6),
        ),
    ]