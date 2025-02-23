from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class GlobalSettings(models.Model):
    markup_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Процент наценки',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    dollar_exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0,  # Например, 1 доллар = 1 доллар
        verbose_name='Курс доллара',
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return "Глобальные настройки"

    class Meta:
        verbose_name = "Глобальная настройка"
        verbose_name_plural = "Глобальные настройки"
