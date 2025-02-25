from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

class GlobalSettings(models.Model):
    global_mark_up = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name='Общий процент наценки',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    dollar_exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100,  # Например, 1 доллар = 1 доллар
        verbose_name='Курс доллара',
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return "Глобальные настройки"

    class Meta:
        verbose_name = "Глобальная настройка"
        verbose_name_plural = "Глобальная настройка"

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def save(self, *args, **kwargs):
        """
        Переопределяем метод save, чтобы предотвратить создание
        нескольких экземпляров этой модели и вернуть сообщение.
        """
        if self.pk is not None:
            # Если объект уже существует, просто обновляем его
            super().save(*args, **kwargs)
        else:
            # Проверяем, существует ли уже экземпляр
            if GlobalSettings.objects.exists():
                # Возвращаем сообщение вместо исключения
                return _("Можно создать только один экземпляр GlobalSettings.")
            super().save(*args, **kwargs)


