# Generated by Django 4.2.4 on 2025-02-25 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('in_progress', 'В работе'), ('completed', 'Собран'), ('delivered', 'Доставлен')], default='pending', max_length=20, verbose_name='Статус'),
        ),
    ]
