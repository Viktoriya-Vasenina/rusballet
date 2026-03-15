from django.db import models
from django.contrib.auth.models import User

class TelegramProfile(models.Model):
    """Профиль пользователя в Telegram"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='telegram_profile',
        verbose_name="Пользователь Django"
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Telegram ID"
    )
    telegram_username = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Username в Telegram"
    )
    verification_code = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Код для привязки"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Telegram подтвержден"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Telegram профиль"
        verbose_name_plural = "Telegram профили"
        db_table = 'bot_telegram_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.telegram_id or 'не привязан'}"
    
    def generate_verification_code(self):
        """Генерирует уникальный код для привязки"""
        import secrets
        self.verification_code = secrets.token_urlsafe(16)
        self.save()
        return self.verification_code