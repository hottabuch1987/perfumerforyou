import uuid
from django.db import models
from users.models import Profile
from product.models import Product
from django.utils import timezone
from math import floor
import random
import string


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('in_progress', 'В работе',),
        ('completed', 'Собран'),
        ('delivered', 'Доставлен'),

    )
    DELIVERY_WAY_CHOICES = [
        ('SDEK', 'SDEK'),
        ('Mail', 'Почта'),
        ('Yandex', 'Яндекс'),
        ('Boxberry', 'Боксберри'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    created = models.DateTimeField("Время заказа", auto_now_add=True)
    updated = models.DateTimeField("Время изменения заказа", auto_now=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    order_number = models.CharField(
        "Номер заказа", 
        max_length=30, 
        unique=True, 
        editable=False
    )
    address_pvz = models.CharField("Адресс ПВЗ", max_length=150)
    delivery = models.CharField("Способ доставки", choices=DELIVERY_WAY_CHOICES, default="SDEK", max_length=150)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.order_number} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        current_date = timezone.now().strftime('%Y%m%d')  # Формат даты: YYYYMMDD
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  # Случайный суффикс
        return f'{current_date}-{random_suffix}'
    
    @property
    def full_name(self):
        return '{} {}'.format(self.user.last_name,
                                 self.user.first_name,
        )


    @property
    def get_total_price(self):
        total = sum(item.get_cost() for item in self.items.all())
        return total

    def delete_completed_orders(self, start_date, end_date):
        """
        Удаляет собранные заказы в указанном диапазоне дат.
        """
        self.objects.filter(status='completed', created__range=(start_date, end_date)).delete()


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='Товар')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Стоимость закупки')
    quantity = models.SmallIntegerField(default=1, verbose_name='Количество')


    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    def __str__(self):
        return str(self.product)

    def get_cost(self):
        # Округление стоимости до десятых с округлением вниз
        return floor(self.price * self.quantity * 10) / 10

