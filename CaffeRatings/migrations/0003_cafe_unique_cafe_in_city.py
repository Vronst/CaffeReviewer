# Generated by Django 5.1 on 2024-09-06 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CaffeRatings', '0002_cafe_approved'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cafe',
            constraint=models.UniqueConstraint(fields=('name', 'city'), name='unique_cafe_in_city'),
        ),
    ]
