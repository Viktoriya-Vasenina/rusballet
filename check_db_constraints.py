import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rusballet_project.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_test_student():
    print("="*50)
    print("СОЗДАНИЕ ТЕСТОВОГО УЧЕНИКА")
    print("="*50)
    
    # Получаем группу Студенты
    students_group, _ = Group.objects.get_or_create(name='Студенты')
    
    # Создаем ученика
    student, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'first_name': 'Тест',
            'last_name': 'Учеников',
            'email': 'test@student.ru',
            'is_staff': False,
            'is_active': True
        }
    )
    
    if created:
        student.set_password('student123')
        student.save()
        student.groups.add(students_group)
        print("✅ Тестовый ученик создан:")
        print(f"   Логин: test_student")
        print(f"   Пароль: student123")
    else:
        print("⚠️ Ученик уже существует")
    
    # Проверяем всех учеников
    print("\n📋 Список учеников:")
    students = User.objects.filter(groups__name='Студенты')
    for s in students:
        print(f"  • {s.username}: {s.first_name} {s.last_name}")

if __name__ == "__main__":
    create_test_student()