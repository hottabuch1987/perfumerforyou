# Generated by Django 4.2.16 on 2025-02-23 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0001_initial'),
        ('users', '0003_profile_markup_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='markup_percentage',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_settings.globalsettings', verbose_name='Процент наценки'),
        ),
    ]
