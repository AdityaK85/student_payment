# Generated by Django 5.1.7 on 2025-03-19 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_auto_20220618_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='password',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
