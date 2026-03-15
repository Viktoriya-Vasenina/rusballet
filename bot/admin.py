from django.contrib import admin
from .models import TelegramProfile

@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'telegram_username', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'telegram_id', 'telegram_username']
    readonly_fields = ['verification_code', 'created_at', 'updated_at']