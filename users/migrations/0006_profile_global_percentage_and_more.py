# Generated by Django 4.2.4 on 2025-02-25 21:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0005_rename_markup_percentage_globalsettings_global_mark_up'),
        ('users', '0005_remove_profile_address_pvz_remove_profile_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='global_percentage',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_settings.globalsettings', verbose_name='Общий процент наценки'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='markup_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Индивидуальный процент наценки'),
        ),
    ]
