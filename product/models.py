from django.db import models
from django.utils import timezone
from supplier.models import Supplier
from app_settings.models import GlobalSettings
import uuid

# Create your models here.
class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products', verbose_name='Поставщик')
    name = models.CharField("Название товара", max_length=100)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    article = models.CharField("Aртикул", max_length=100)
    is_visible = models.BooleanField("Видимость", default=True)
    quantity = models.PositiveIntegerField("Количество товара", default=1)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    def __str__(self):
        return f"Потсавщик: {self.supplier.name}; Товар: {self.name}" if self.supplier else self.name
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['name'], name='name_idx'),  # Индекс по полю name
            models.Index(fields=['article'], name='article_idx'),  # Индекс по полю article
            models.Index(fields=['price'], name='price_idx'),  # Индекс по полю price
        ]
