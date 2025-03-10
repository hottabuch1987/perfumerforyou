# Generated by Django 4.2.16 on 2025-02-23 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Профиль', 'verbose_name_plural': 'Профили'},
        ),
        migrations.AddIndex(
            model_name='profile',
            index=models.Index(fields=['last_name'], name='flast_name_idx'),
        ),
        migrations.AddIndex(
            model_name='profile',
            index=models.Index(fields=['phone_number'], name='phone_number_idx'),
        ),
    ]
