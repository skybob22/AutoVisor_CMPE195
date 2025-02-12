# Generated by Django 3.1.2 on 2020-11-16 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0023_student_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='friendRequests',
        ),
        migrations.RemoveField(
            model_name='student',
            name='friends',
        ),
        migrations.RemoveField(
            model_name='student',
            name='prefCourseList',
        ),
        migrations.AlterField(
            model_name='student',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='student',
            name='studentID',
            field=models.CharField(max_length=9),
        ),
        migrations.DeleteModel(
            name='PreferredCourse',
        ),
    ]
