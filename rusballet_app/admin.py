from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from django.urls import reverse
from .models import Group, Schedule, Booking

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):  # Убрали HierarchicalModelAdmin
    list_display = ['name', 'age_range', 'teacher_name', 'view_schedule', 'view_bookings', 'order', 'is_active']
    list_filter = ['is_active', 'teacher']
    search_fields = ['name', 'description', 'teacher__first_name', 'teacher__last_name']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    
    # Убрали hierarchy = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='Администраторы').exists():
            return qs
        if request.user.groups.filter(name='Учителя').exists():
            return qs.filter(teacher=request.user)
        return qs.none()
    
    def age_range(self, obj):
        return f"{obj.age_min}-{obj.age_max} лет"
    age_range.short_description = "Возраст"
    
    def teacher_name(self, obj):
        if obj.teacher:
            return f"{obj.teacher.last_name} {obj.teacher.first_name}"
        return "—"
    teacher_name.short_description = "Преподаватель"
    
    def view_schedule(self, obj):
        url = reverse('admin:rusballet_app_schedule_changelist')
        return format_html(
            '<a class="button" href="{}?group__id__exact={}" style="background-color: #79aec8; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;">📅 Расписание</a>',
            url, obj.id
        )
    view_schedule.short_description = ""
    
    def view_bookings(self, obj):
        url = reverse('admin:rusballet_app_booking_changelist')
        return format_html(
            '<a class="button" href="{}?schedule__group__id__exact={}" style="background-color: #417690; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;">📝 Записи</a>',
            url, obj.id
        )
    view_bookings.short_description = ""
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Администраторы').exists():
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Администраторы').exists():
            return True
        return False

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'group_link', 'teacher_name', 'seats_info', 'is_trial', 'view_bookings', 'is_active']
    list_filter = [
        ('date', DateFieldListFilter),
        'group__teacher',
        'group',
        'is_trial',
        'is_active',
    ]
    search_fields = ['group__name', 'group__teacher__last_name', 'group__teacher__first_name']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
    list_editable = ['is_active']
    list_per_page = 50
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='Администраторы').exists():
            return qs
        if request.user.groups.filter(name='Учителя').exists():
            return qs.filter(group__teacher=request.user)
        return qs.none()
    
    def group_link(self, obj):
        url = reverse('admin:rusballet_app_group_change', args=[obj.group.id])
        return format_html('<a href="{}">{}</a>', url, obj.group.name)
    group_link.short_description = "Группа"
    group_link.admin_order_field = 'group__name'
    
    def teacher_name(self, obj):
        if obj.group.teacher:
            return f"{obj.group.teacher.last_name} {obj.group.teacher.first_name}"
        return "—"
    teacher_name.short_description = "Преподаватель"
    teacher_name.admin_order_field = 'group__teacher__last_name'
    
    def seats_info(self, obj):
        free = obj.max_seats - obj.booked_seats
        if free > 3:
            color = 'green'
        elif free > 0:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{obj.booked_seats}/{obj.max_seats}</span> (свободно: {free})'
        )
    seats_info.short_description = "Места"
    
    def view_bookings(self, obj):
        url = reverse('admin:rusballet_app_booking_changelist')
        count = obj.bookings.count()
        return format_html(
            '<a class="button" href="{}?schedule__id__exact={}" style="background-color: #417690; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;">📝 {} записей</a>',
            url, obj.id, count
        )
    view_bookings.short_description = ""
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Администраторы').exists():
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Администраторы').exists():
            return True
        return False

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'child_name', 'child_age', 'schedule_link', 'teacher_name', 'status', 'status_colored', 'edit_link', 'created_at']
    list_filter = [
        'status',
        ('created_at', DateFieldListFilter),
        ('schedule__date', DateFieldListFilter),
        'schedule__group__teacher',
        'schedule__group',
    ]
    search_fields = ['full_name', 'phone', 'child_name', 'schedule__group__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_editable = ['status']
    list_per_page = 50
    date_hierarchy = 'schedule__date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='Администраторы').exists():
            return qs
        if request.user.groups.filter(name='Учителя').exists():
            return qs.filter(schedule__group__teacher=request.user)
        return qs.none()
    
    def schedule_link(self, obj):
        url = reverse('admin:rusballet_app_schedule_change', args=[obj.schedule.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, f"{obj.schedule.date.strftime('%d.%m')} {obj.schedule.start_time.strftime('%H:%M')}"
        )
    schedule_link.short_description = "Занятие"
    
    def teacher_name(self, obj):
        if obj.schedule.group.teacher:
            return f"{obj.schedule.group.teacher.last_name} {obj.schedule.group.teacher.first_name}"
        return "—"
    teacher_name.short_description = "Преподаватель"
    
    def status_colored(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#28A745',
            'cancelled': '#DC3545',
            'completed': '#007BFF',
        }
        color = colors.get(obj.status, '#000000')
        status_display = dict(obj.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(f'<span style="color: {color}; font-weight: bold;">{status_display}</span>')
    status_colored.short_description = "Статус"
    
    def edit_link(self, obj):
        url = reverse('admin:rusballet_app_booking_change', args=[obj.id])
        return format_html('<a href="{}">✏️</a>', url)
    edit_link.short_description = ""
    
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']
    
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "✅ Подтвердить выбранные записи"
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "✅ Отметить как проведенные"
    
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "❌ Отменить выбранные записи"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Администраторы').exists():
            return True
        return False