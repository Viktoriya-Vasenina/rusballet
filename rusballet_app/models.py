from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(
        max_length=100, 
        verbose_name="Название группы"
    )
    
    description = models.TextField(
        verbose_name="Описание группы",
        blank=True 
    )

    age_min = models.IntegerField(
        verbose_name="Минимальный возраст",
        null=True,  # ДОБАВЛЕНО
        blank=True  # ДОБАВЛЕНО
    )
    
    age_max = models.IntegerField(
        verbose_name="Максимальный возраст",
        null=True,  # ДОБАВЛЕНО
        blank=True  # ДОБАВЛЕНО
    )

    order = models.IntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна для записи"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Преподаватель",
        related_name='teaching_groups'
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ['order', 'age_min']  
    
    def __str__(self):
        if self.age_min and self.age_max:
            return f"{self.name} ({self.age_min}-{self.age_max} лет)"
        return self.name
    
    def get_age_range(self):
        if self.age_min and self.age_max:
            return f"{self.age_min}-{self.age_max} лет"
        return "Возраст не указан"

class Schedule(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name="Группа",
        related_name='schedules'
    )

    date = models.DateField(
        verbose_name="Дата занятия"
    )

    start_time = models.TimeField(
        verbose_name="Время начала"
    )

    duration = models.IntegerField(
        verbose_name="Длительность (минуты)",
        default=60, 
        help_text="Продолжительность занятия в минутах"
    )

    max_seats = models.IntegerField(
        verbose_name="Максимальное количество мест",
        default=10
    )

    booked_seats = models.IntegerField(
        verbose_name="Занято мест",
        default=0
    )

    is_active = models.BooleanField(
        verbose_name="Активно для записи",
        default=True
    )

    is_trial = models.BooleanField(
        verbose_name="Пробное занятие",
        default=False,
        help_text="Отмечать, если это пробное занятие (доступно для записи через бота/сайт)"
    )

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
        ordering = ['date', 'start_time']
        unique_together = ['group', 'date', 'start_time']
    
    def __str__(self):
        trial_mark = " (Пробное)" if self.is_trial else ""
        return f"{self.date} {self.start_time} - {self.group.name}{trial_mark}"
    
    def get_end_time(self):
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = start + timedelta(minutes=self.duration)
        return end.time()
    
    def get_free_seats(self):
        return self.max_seats - self.booked_seats
    
    def is_available(self):
        return self.is_active and self.get_free_seats() > 0

class Booking(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        verbose_name="Расписание",
        related_name='bookings'
    )
    
    full_name = models.CharField(
        max_length=200,
        verbose_name="ФИО родителя"
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )
    
    child_name = models.CharField(
        max_length=100,
        verbose_name="Имя ребенка"
    )
    
    child_age = models.IntegerField(
        verbose_name="Возраст ребенка"
    )
    
    notes = models.TextField(
        verbose_name="Дополнительные заметки",
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания записи"
    )
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Занятие проведено'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус записи"
    )

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ['-created_at']
    
    def __str__(self):
        trial_mark = " (Пробное)" if self.schedule.is_trial else ""
        return f"{self.full_name} - {self.child_name} ({self.schedule.date} {self.schedule.start_time}){trial_mark}"
    
class StudentProfile(models.Model):
    """Профиль ученика для хранения дополнительной информации"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name="Пользователь"
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Группа"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        blank=True
    )
    age = models.IntegerField(  # НОВОЕ ПОЛЕ
        verbose_name="Возраст",
        null=True,
        blank=True,
        help_text="Возраст ученика (для контроля выпуска)"
    )
    
    class Meta:
        verbose_name = "Профиль ученика"
        verbose_name_plural = "Профили учеников"
    
    def __str__(self):
        age_str = f", {self.age} лет" if self.age else ""
        return f"{self.user.get_full_name()} - {self.group.name if self.group else 'Нет группы'}{age_str}"