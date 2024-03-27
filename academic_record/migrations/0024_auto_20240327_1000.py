# Generated by Django 3.2 on 2024-03-27 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic_record', '0023_rename_date_attendance_attendance_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academicyear',
            options={'ordering': ['created_at']},
        ),
        migrations.AddField(
            model_name='schedule',
            name='is_view_grade',
            field=models.BooleanField(default=False),
        ),
    ]
