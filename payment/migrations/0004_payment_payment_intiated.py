# Generated by Django 5.1.5 on 2025-03-21 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_payment_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_intiated',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
