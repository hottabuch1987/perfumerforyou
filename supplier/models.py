from django.db import models
from django.core.validators import RegexValidator


# Create your models here.
class Supplier(models.Model):
    name = models.CharField("Название поставщика", max_length=100)
    email = models.EmailField('Email', unique=True, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            message="Некорректный email."
        )
    ])
    created = models.DateTimeField("Время Создания поставщика", auto_now_add=True)
    updated = models.DateTimeField("Время последнего обновления", auto_now=True)

    def __str__(self):
        return f"Поставщик: {self.name}; Email: {self.email}"
    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

