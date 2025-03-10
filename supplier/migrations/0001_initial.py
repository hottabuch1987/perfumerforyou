# Generated by Django 4.2.16 on 2025-02-23 09:46

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название поставщика')),
                ('email', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.RegexValidator(message='Некорректный email.', regex='^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$')], verbose_name='Email')),
                ('is_visible', models.BooleanField(default=True, verbose_name='Видимость товаров поставщика')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время Создания поставщика')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Время последнего обновления')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suppliers', to='product.product', verbose_name='Товар')),
            ],
        ),
    ]
