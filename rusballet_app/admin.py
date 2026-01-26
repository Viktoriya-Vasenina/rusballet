from django.contrib import admin
from .models import Group, Schedule, Booking

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'age_min', 'age_max', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'group', 'max_seats', 'booked_seats', 'is_active']
    list_filter = ['date', 'group', 'is_active']
    search_fields = ['group__name']
    date_hierarchy = 'date'
    ordering = ['-date', 'start_time']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'child_name', 'schedule', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'schedule__group']
    search_fields = ['full_name', 'child_name', 'phone']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
