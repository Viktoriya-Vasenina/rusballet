import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rusballet_project.settings')
django.setup()

from rusballet_app.models import Group, Schedule

def update_schedule():
    print("🔄 ОБНОВЛЕНИЕ РАСПИСАНИЯ")
    print("=" * 40)
    
    deleted_count = Schedule.objects.filter(date__year=2026, date__month=2).delete()[0]
    print(f"🗑️ Удалено старых записей: {deleted_count}")
    
    year = 2026
    month = 2
    
    saturdays = [
        datetime.date(year, month, 7),
        datetime.date(year, month, 14),
        datetime.date(year, month, 21),
        datetime.date(year, month, 28)
    ]
    
    time_slots = [
        datetime.time(10, 0),
        datetime.time(14, 0),
        datetime.time(17, 0)
    ]
    
    groups = Group.objects.all()
    created_count = 0
    
    for saturday in saturdays:
        for start_time in time_slots:
            for group in groups:
                Schedule.objects.create(
                    group=group,
                    date=saturday,
                    start_time=start_time,
                    duration=60,
                    max_seats=5,
                    booked_seats=0,
                    is_active=True
                )
                created_count += 1
    
    print(f"✅ Создано новых записей: {created_count}")
    print(f"📅 Субботы: 7, 14, 21, 28 февраля 2026")
    print(f"🕒 Время: 10:00, 14:00, 17:00")
    print(f"👥 Группы: {groups.count()}")
    print(f"🎟️ Мест в каждом занятии: 5")
    print(f"📊 Всего возможных записей: {created_count * 5}")
    print("=" * 40)
    print("✅ Расписание обновлено!")

if __name__ == "__main__":
    update_schedule()