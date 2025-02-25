import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import User
from app_settings.models import GlobalSettings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class Profile(models.Model):
    DELIVERY_WAY_CHOICES = [
        ('SDEK', 'SDEK'),
        ('Mail', 'Почта'),
        ('Yandex', 'Яндекс'),
        ('Boxberry', 'Боксберри'),
    ]
    CURRENCY_CHOICES = [
        ('RUB', 'Рубль'),
        ('USD', 'Доллар'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Связь один-к-одному с моделью User
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    first_name = models.CharField(
        max_length=20,
        verbose_name='Имя',
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        }
    )
    last_name = models.CharField(
        max_length=20,
        verbose_name='Фамилия',
        null=True,
        blank=True
    )
    last_login = models.DateTimeField(
        verbose_name='Время последнего входа',
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        'Телефон',
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+7\d{10}$',
                message="Номер телефона должен быть в формате: '+79991234567'."
            )
        ]
    )
    
    markup_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Индивидуальный процент наценки',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='RUB',
        verbose_name='Валюта'
    )

    
    def save(self, *args, **kwargs):
        if not self.first_name:
            self.first_name = generate_unique_username()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Профиль {self.user.username}'
    
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        indexes = [
            models.Index(fields=['last_name'], name='flast_name_idx'),  # Индекс по полю last_name для поиска
            models.Index(fields=['phone_number'], name='phone_number_idx'),  # Индекс по полю phone_number для поиска
        ]
        
    

def generate_unique_username(base: str = "user", length: int = 12) -> str:
    """
    Генерирует уникальное имя пользователя с указанным базовым префиксом и случайным суффиксом.
    
    :param base: Базовое имя пользователя (по умолчанию "user").
    :param length: Длина случайной части имени (по умолчанию 12 символов).
    :return: Уникальное имя пользователя в формате "user_xxxxxxxxxxxx".
    """
    suffix_pool = string.ascii_lowercase + string.digits

    while True:
        # Генерируем случайный суффикс
        suffix = ''.join(random.choices(suffix_pool, k=length))
        username = f"{base}_{suffix}"

        # Проверяем его уникальность в базе данных
        if not User.objects.filter(username=username).exists():
            return username
