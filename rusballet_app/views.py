from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Count
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group as AuthGroup
from django.core.exceptions import ValidationError
import json
from datetime import date, timedelta
from .models import Group as BalletGroup, Schedule, Booking, StudentProfile
from bot.models import TelegramProfile

def home(request):
    """Главная страница сайта"""
    return render(request, 'home.html')

def api_groups(request):
    groups = BalletGroup.objects.filter(is_active=True)
    data = [{
        'id': g.id,
        'name': g.name,
        'age_range': g.get_age_range()
    } for g in groups]
    return JsonResponse({'groups': data})

def api_schedule(request):
    group_id = request.GET.get('group_id')
    
    if not group_id:
        return JsonResponse({'error': 'Укажите group_id'}, status=400)
    
    schedules = Schedule.objects.filter(
        group_id=group_id,
        is_active=True,
        is_trial=True
    )
    
    data = []
    for s in schedules:
        data.append({
            'id': s.id,
            'date': s.date.strftime('%Y-%m-%d'),
            'time': s.start_time.strftime('%H:%M'),
            'free_seats': s.max_seats - s.booked_seats,
            'max_seats': s.max_seats
        })
    
    return JsonResponse({'schedule': data})

@csrf_exempt
def api_create_booking(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        schedule = Schedule.objects.get(id=data['schedule_id'])
        if not schedule.is_trial:
            return JsonResponse({'error': 'Можно записываться только на пробные занятия'}, status=400)
        
        booking = Booking.objects.create(
            schedule_id=data['schedule_id'],
            full_name=data['full_name'],
            phone=data['phone'],
            child_name=data['child_name'],
            child_age=data['child_age'],
            notes=data.get('notes', '')
        )
        
        Schedule.objects.filter(id=data['schedule_id']).update(
            booked_seats=F('booked_seats') + 1
        )
        
        return JsonResponse({'success': True, 'booking_id': booking.id})
    
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Занятие не найдено'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def telegram_bind(request):
    profile, created = TelegramProfile.objects.get_or_create(
        user=request.user,
        defaults={'is_verified': False}
    )
    
    if not profile.verification_code:
        profile.generate_verification_code()
    
    context = {
        'verification_code': profile.verification_code,
        'bot_username': 'rusballet_bot',
    }
    
    return render(request, 'telegram_bind.html', context)

# ========== КАСТОМНАЯ АДМИН-ПАНЕЛЬ ==========

def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, 'У вас нет прав доступа к админке')
    else:
        form = AuthenticationForm()
    
    return render(request, 'admin/login.html', {'form': form})

def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')

@login_required
@staff_member_required
def admin_dashboard(request):
    today = date.today()
    
    total_teachers = User.objects.filter(groups__name='Учителя').count()
    total_students = User.objects.filter(groups__name='Студенты').count()
    total_groups = BalletGroup.objects.filter(is_active=True).count()
    
    today_schedule_count = Schedule.objects.filter(
        date=today, 
        is_active=True
    ).count()
    
    trial_bookings_count = Booking.objects.filter(
        schedule__is_trial=True,
        schedule__date__gte=today,
        status__in=['pending', 'confirmed']
    ).count()
    
    # ИСПРАВЛЕНО: только пробные занятия и последние 10
    recent_bookings = Booking.objects.filter(
        schedule__is_trial=True  # Только пробные занятия
    ).select_related(
        'schedule', 'schedule__group', 'schedule__group__teacher'
    ).order_by('-created_at')[:10]
    
    today_schedules = Schedule.objects.filter(
        date=today,
        is_active=True
    ).select_related('group', 'group__teacher').order_by('start_time')
    
    context = {
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_groups': total_groups,
        'today_schedule': today_schedule_count,
        'trial_bookings': trial_bookings_count,
        'recent_bookings': recent_bookings,
        'today_schedules': today_schedules,
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
@staff_member_required
def admin_teachers(request):
    """Список преподавателей"""
    teachers = User.objects.filter(groups__name='Учителя').prefetch_related('teaching_groups')
    groups = BalletGroup.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'admin/teachers.html', {
        'teachers': teachers,
        'groups': groups
    })

@login_required
@staff_member_required
def admin_students(request):
    """Список учеников"""
    students = User.objects.filter(
        groups__name='Студенты'
    ).select_related('student_profile', 'student_profile__group')
    
    groups = BalletGroup.objects.filter(is_active=True).order_by('name')
    
    print(f"📊 Найдено учеников: {students.count()}")
    
    return render(request, 'admin/students.html', {
        'students': students,
        'groups': groups
    })

@login_required
@staff_member_required
def admin_schedule(request):
    schedules = Schedule.objects.select_related(
        'group', 'group__teacher'
    ).filter(is_active=True).order_by('date', 'group__name', 'start_time')
    
    group_id = request.GET.get('group')
    teacher_id = request.GET.get('teacher')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    is_trial = request.GET.get('is_trial')
    
    if group_id:
        schedules = schedules.filter(group_id=group_id)
    if teacher_id:
        schedules = schedules.filter(group__teacher_id=teacher_id)
    if date_from:
        schedules = schedules.filter(date__gte=date_from)
    if date_to:
        schedules = schedules.filter(date__lte=date_to)
    if is_trial:
        schedules = schedules.filter(is_trial=(is_trial == 'true'))
    
    # Получаем все активные группы
    groups = BalletGroup.objects.filter(is_active=True).order_by('name')
    teachers = User.objects.filter(groups__name='Учителя').order_by('last_name')
    
    print(f"📊 Найдено групп: {groups.count()}")  # Отладка в консоль Python
    
    context = {
        'schedules': schedules,
        'groups': groups,  # Убедитесь, что это здесь
        'teachers': teachers,
        'today': date.today(),
        'next_week': date.today() + timedelta(days=7),
    }
    return render(request, 'admin/schedule.html', context)
@login_required
@staff_member_required
def admin_bookings(request):
    bookings = Booking.objects.select_related(
        'schedule', 'schedule__group', 'schedule__group__teacher'
    ).order_by('-created_at')
    
    status = request.GET.get('status')
    group_id = request.GET.get('group')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        bookings = bookings.filter(status=status)
    if group_id:
        bookings = bookings.filter(schedule__group_id=group_id)
    if date_from:
        bookings = bookings.filter(schedule__date__gte=date_from)
    if date_to:
        bookings = bookings.filter(schedule__date__lte=date_to)
    
    groups = BalletGroup.objects.filter(is_active=True)
    
    context = {
        'bookings': bookings[:100],
        'groups': groups,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'admin/bookings.html', context)

@login_required
@staff_member_required
def admin_trial_bookings(request):
    trial_bookings = Booking.objects.filter(
        schedule__is_trial=True
    ).select_related(
        'schedule', 'schedule__group', 'schedule__group__teacher'
    ).order_by('schedule__date', 'schedule__start_time')
    
    context = {
        'trial_bookings': trial_bookings,
    }
    return render(request, 'admin/trial_bookings.html', context)

@login_required
@staff_member_required
def admin_group_detail(request, group_id):
    group = BalletGroup.objects.get(id=group_id)
    schedules = Schedule.objects.filter(
        group=group,
        is_active=True
    ).order_by('date', 'start_time')
    
    context = {
        'group': group,
        'schedules': schedules,
    }
    return render(request, 'admin/group_detail.html', context)

@login_required
@staff_member_required
def admin_teacher_detail(request, teacher_id):
    try:
        teacher = User.objects.get(id=teacher_id, groups__name='Учителя')
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("Преподаватель не найден")
    
    groups = teacher.teaching_groups.all()
    
    context = {
        'teacher': teacher,
        'groups': groups,
    }
    return render(request, 'admin/teacher_detail.html', context)

@login_required
@staff_member_required
def admin_teacher_groups(request, teacher_id):
    try:
        teacher = User.objects.get(id=teacher_id, groups__name='Учителя')
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("Преподаватель не найден")
    
    groups = teacher.teaching_groups.all()
    
    context = {
        'teacher': teacher,
        'groups': groups,
    }
    return render(request, 'admin/teacher_groups.html', context)

@login_required
@staff_member_required
def admin_teacher_schedule(request, teacher_id):
    try:
        teacher = User.objects.get(id=teacher_id, groups__name='Учителя')
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("Преподаватель не найден")
    
    schedules = Schedule.objects.filter(
        group__teacher=teacher,
        is_active=True
    ).select_related('group').order_by('date', 'start_time')
    
    context = {
        'teacher': teacher,
        'schedules': schedules,
    }
    return render(request, 'admin/teacher_schedule.html', context)

@login_required
@staff_member_required
def admin_groups(request):
    """Список групп"""
    groups = BalletGroup.objects.all().select_related('teacher').prefetch_related('students')
    teachers = User.objects.filter(groups__name='Учителя', is_active=True)
    
    return render(request, 'admin/groups.html', {
        'groups': groups,
        'teachers': teachers
    })

# ========== API ДЛЯ AJAX ЗАПРОСОВ ==========

@csrf_exempt
@login_required
@staff_member_required
def api_update_booking_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body)
        booking = Booking.objects.get(id=data['booking_id'])
        booking.status = data['status']
        booking.save()
        
        return JsonResponse({'success': True})
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# API для преподавателей
@csrf_exempt
@login_required
@staff_member_required
def api_save_teacher(request):
    """Сохранение преподавателя (создание или редактирование)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST метод разрешен'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("="*50)
        print("📥 СОХРАНЕНИЕ ПРЕПОДАВАТЕЛЯ:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        
        teacher_id = data.get('teacher_id')
        username = data.get('username', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        is_active = data.get('is_active') == 'active'
        group_id = data.get('group_id')
        
        if not username or not first_name or not last_name:
            return JsonResponse({'error': 'Заполните имя, фамилию и логин'}, status=400)
        
        teachers_group, _ = AuthGroup.objects.get_or_create(name='Учителя')
        
        if teacher_id:
            try:
                teacher = User.objects.get(id=teacher_id)
                
                if teacher.username != username and User.objects.filter(username=username).exists():
                    return JsonResponse({'error': 'Логин уже занят'}, status=400)
                
                teacher.username = username
                teacher.first_name = first_name
                teacher.last_name = last_name
                teacher.email = email
                teacher.is_staff = True
                teacher.is_active = is_active
                
                if password:
                    teacher.set_password(password)
                
                teacher.save()
                teacher.groups.add(teachers_group)
                
                if group_id and group_id.strip():
                    try:
                        group_id_int = int(group_id)
                        group = BalletGroup.objects.get(id=group_id_int)
                        BalletGroup.objects.filter(teacher=teacher).update(teacher=None)
                        group.teacher = teacher
                        group.save()
                    except (ValueError, BalletGroup.DoesNotExist):
                        pass
                else:
                    BalletGroup.objects.filter(teacher=teacher).update(teacher=None)
                
                return JsonResponse({'success': True, 'id': teacher.id})
                
            except User.DoesNotExist:
                return JsonResponse({'error': 'Преподаватель не найден'}, status=404)
        
        else:
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Логин уже занят'}, status=400)
            
            if not password:
                return JsonResponse({'error': 'Пароль обязателен'}, status=400)
            
            teacher = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=True,
                is_active=is_active
            )
            
            teacher.groups.add(teachers_group)
            
            if group_id and group_id.strip():
                try:
                    group_id_int = int(group_id)
                    group = BalletGroup.objects.get(id=group_id_int)
                    group.teacher = teacher
                    group.save()
                except (ValueError, BalletGroup.DoesNotExist):
                    pass
            
            return JsonResponse({'success': True, 'id': teacher.id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_update_teacher_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body)
        teacher_ids = data.get('teacher_ids', [])
        is_active = data.get('is_active', True)
        
        User.objects.filter(id__in=teacher_ids).update(is_active=is_active)
        return JsonResponse({'success': True, 'count': len(teacher_ids)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# API для учеников
@csrf_exempt
@login_required
@staff_member_required
def api_save_student(request):
    """Сохранение ученика (создание или редактирование)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST метод разрешен'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("="*50)
        print("📥 СОХРАНЕНИЕ УЧЕНИКА:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        
        student_id = data.get('student_id')
        username = data.get('username', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        age = data.get('age')
        password = data.get('password', '')
        is_active = data.get('is_active', True)
        group_id = data.get('group_id')
        
        print(f"📊 Данные: логин={username}, имя={first_name}, фамилия={last_name}, тел={phone}, возраст={age}, группа={group_id}")
        
        if not username or not first_name or not last_name:
            return JsonResponse({'error': 'Заполните имя, фамилию и логин'}, status=400)
        
        # ПРОВЕРКА СООТВЕТСТВИЯ ВОЗРАСТА И ГРУППЫ
        if group_id and group_id.strip() and age:
            try:
                group = BalletGroup.objects.get(id=int(group_id))
                if group.age_min and group.age_max:
                    age_int = int(age)
                    if age_int < group.age_min or age_int > group.age_max:
                        return JsonResponse({
                            'error': f'Возраст ученика ({age} лет) не соответствует группе "{group.name}" ({group.age_min}-{group.age_max} лет)'
                        }, status=400)
                    else:
                        print(f"✅ Возраст {age} лет соответствует группе {group.name}")
            except (ValueError, BalletGroup.DoesNotExist) as e:
                print(f"⚠️ Не удалось проверить группу: {e}")
        
        students_group, _ = AuthGroup.objects.get_or_create(name='Студенты')
        
        if student_id:  # РЕДАКТИРОВАНИЕ
            try:
                student = User.objects.get(id=student_id)
                print(f"👤 Редактирование ученика: {student.username} (ID: {student_id})")
                
                if student.username != username and User.objects.filter(username=username).exists():
                    return JsonResponse({'error': 'Логин уже занят'}, status=400)
                
                student.username = username
                student.first_name = first_name
                student.last_name = last_name
                student.email = email
                student.is_staff = False
                student.is_active = is_active
                
                if password:
                    student.set_password(password)
                    print("  🔑 Пароль обновлен")
                
                student.save()
                student.groups.add(students_group)
                print("  ✅ Ученик сохранен")
                
                student_profile, profile_created = StudentProfile.objects.get_or_create(user=student)
                
                student_profile.phone = phone
                if age:
                    try:
                        student_profile.age = int(age) if age else None
                        print(f"  ✅ Возраст сохранен: {age}")
                    except ValueError:
                        print(f"  ⚠️ Ошибка преобразования возраста: {age}")
                        student_profile.age = None
                
                # ===== РАБОТА С ГРУППОЙ =====
                print(f"\n🔍 Назначение группы ученику:")
                print(f"   group_id: '{group_id}'")
                
                if group_id and group_id.strip():
                    try:
                        group_id_int = int(group_id)
                        print(f"   Поиск группы с ID: {group_id_int}")
                        
                        group = BalletGroup.objects.get(id=group_id_int)
                        student_profile.group = group
                        print(f"   ✅ Группа '{group.name}' назначена ученику")
                        
                    except ValueError:
                        print(f"   ❌ Ошибка: group_id не число")
                        student_profile.group = None
                    except BalletGroup.DoesNotExist:
                        print(f"   ❌ Ошибка: группа не найдена")
                        student_profile.group = None
                else:
                    print(f"   📌 Группа не выбрана, очищаем")
                    student_profile.group = None
                
                student_profile.save()
                print(f"  ✅ Профиль ученика сохранен")
                
                return JsonResponse({'success': True, 'id': student.id})
                
            except User.DoesNotExist:
                return JsonResponse({'error': 'Ученик не найден'}, status=404)
        
        else:  # СОЗДАНИЕ
            print(f"👤 Создание нового ученика: {username}")
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Логин уже занят'}, status=400)
            
            if not password:
                return JsonResponse({'error': 'Пароль обязателен'}, status=400)
            
            student = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=False,
                is_active=is_active
            )
            print(f"  ✅ Пользователь создан (ID: {student.id})")
            
            student.groups.add(students_group)
            print("  ✅ Добавлен в группу 'Студенты'")
            
            profile_data = {'user': student, 'phone': phone}
            if age:
                try:
                    profile_data['age'] = int(age) if age else None
                    print(f"  ✅ Возраст будет сохранен: {age}")
                except ValueError:
                    print(f"  ⚠️ Ошибка преобразования возраста: {age}")
            
            student_profile = StudentProfile.objects.create(**profile_data)
            
            # ===== РАБОТА С ГРУППОЙ =====
            print(f"\n🔍 Назначение группы ученику:")
            print(f"   group_id: '{group_id}'")
            
            if group_id and group_id.strip():
                try:
                    group_id_int = int(group_id)
                    print(f"   Поиск группы с ID: {group_id_int}")
                    
                    group = BalletGroup.objects.get(id=group_id_int)
                    student_profile.group = group
                    student_profile.save()
                    print(f"   ✅ Группа '{group.name}' назначена ученику")
                    
                except ValueError:
                    print(f"   ❌ Ошибка: group_id не число")
                except BalletGroup.DoesNotExist:
                    print(f"   ❌ Ошибка: группа не найдена")
            else:
                print(f"   📌 Группа не выбрана")
            
            return JsonResponse({'success': True, 'id': student.id})
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_update_student_status(request):
    """Массовое обновление статуса учеников"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body)
        student_ids = data.get('student_ids', [])
        is_active = data.get('is_active', True)
        
        User.objects.filter(id__in=student_ids).update(is_active=is_active)
        return JsonResponse({'success': True, 'count': len(student_ids)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@staff_member_required
def api_get_student_group(request, student_id):
    """Получение группы ученика"""
    try:
        student = User.objects.get(id=student_id)
        try:
            profile = StudentProfile.objects.get(user=student)
            group_id = profile.group.id if profile.group else None
        except StudentProfile.DoesNotExist:
            group_id = None
            
        return JsonResponse({'group_id': group_id})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Ученик не найден'}, status=404)
    
@csrf_exempt
@login_required
@staff_member_required
def api_confirm_trial_booking(request):
    """Подтверждение пробной заявки и создание ученика"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("="*50)
        print("📥 ПОДТВЕРЖДЕНИЕ ЗАЯВКИ:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        
        booking_id = data.get('booking_id')
        full_name = data.get('full_name')
        phone = data.get('phone')
        child_name = data.get('child_name')
        child_age = data.get('child_age')
        group_id = data.get('group_id')
        
        # Получаем заявку
        booking = Booking.objects.get(id=booking_id)
        
        # Разбираем ФИО на имя и фамилию
        name_parts = full_name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[1]
            last_name = name_parts[0]
        else:
            first_name = full_name
            last_name = ''
        
        # Транслитерация для логина
        def transliterate(text):
            translit_dict = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            }
            result = ''
            for char in text:
                result += translit_dict.get(char, char)
            return result
        
        # Генерируем логин
        base_username = transliterate(f"{last_name}_{first_name}".lower())
        base_username = ''.join(c for c in base_username if c.isalnum() or c == '_')
        
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Создаем пользователя
        student = User.objects.create_user(
            username=username,
            password='',
            first_name=first_name,
            last_name=last_name,
            email='',
            is_staff=False,
            is_active=True
        )
        
        # Добавляем в группу Студенты
        students_group, _ = AuthGroup.objects.get_or_create(name='Студенты')
        student.groups.add(students_group)
        
        # Создаем профиль ученика
        student_profile = StudentProfile.objects.create(
            user=student,
            phone=phone
        )
        
        # Назначаем группу, если указана
        if group_id:
            try:
                group = BalletGroup.objects.get(id=int(group_id))
                student_profile.group = group
                student_profile.save()
            except (ValueError, BalletGroup.DoesNotExist):
                pass
        
        # Обновляем статус заявки
        booking.status = 'confirmed'
        booking.save()
        
        return JsonResponse({
            'success': True,
            'username': username,
            'message': f'Ученик создан. Логин: {username}'
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Заявка не найдена'}, status=404)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
@login_required
@staff_member_required
def api_cancel_trial_booking(request):
    """Отмена заявки и принудительное удаление ученика из БД"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        booking_id = data.get('booking_id')
        
        print(f"\n🔴 НАЧАЛО ОТМЕНЫ ЗАЯВКИ ID: {booking_id}")
        
        # Получаем заявку
        booking = Booking.objects.get(id=booking_id)
        print(f"📌 Заявка: {booking.full_name}, статус: {booking.status}")
        print(f"📌 Телефон: {booking.phone}")
        
        # ВСЕГДА удаляем ученика, независимо от статуса (для теста)
        print("\n🔍 НАЧИНАЕМ ПОИСК УЧЕНИКА...")
        
        # Ищем профиль по телефону
        profiles = StudentProfile.objects.filter(phone=booking.phone)
        print(f"📌 Найдено профилей с телефоном {booking.phone}: {profiles.count()}")
        
        for profile in profiles:
            user = profile.user
            print(f"\n👤 Найден пользователь: {user.username}")
            print(f"   Имя: {user.first_name}")
            print(f"   Фамилия: {user.last_name}")
            print(f"   ID пользователя: {user.id}")
            print(f"   ID профиля: {profile.id}")
            
            # Принудительно удаляем
            try:
                profile.delete()
                print(f"   ✅ Профиль удален")
                
                user.delete()
                print(f"   ✅ Пользователь удален")
            except Exception as e:
                print(f"   ❌ Ошибка при удалении: {e}")
        
        # Меняем статус заявки
        booking.status = 'cancelled'
        booking.save()
        print(f"✅ Статус заявки изменен на cancelled")
        
        # Проверяем, остался ли ученик
        remaining = StudentProfile.objects.filter(phone=booking.phone).count()
        print(f"📌 Осталось профилей с телефоном {booking.phone}: {remaining}")
        
        return JsonResponse({'success': True})
        
    except Booking.DoesNotExist:
        print(f"❌ Заявка {booking_id} не найдена")
        return JsonResponse({'error': 'Заявка не найдена'}, status=404)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)

# API для групп
@csrf_exempt
@login_required
@staff_member_required
def api_save_group(request):
    """Сохранение группы (создание или редактирование)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST метод разрешен'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("="*50)
        print("📥 СОХРАНЕНИЕ ГРУППЫ:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*50)
        
        group_id = data.get('group_id')
        name = data.get('name', '').strip()
        age_min = data.get('age_min')
        age_max = data.get('age_max')
        teacher_id = data.get('teacher_id')
        is_active = data.get('is_active', True)
        
        if not name or not age_min or not age_max:
            return JsonResponse({'error': 'Заполните название и возраст'}, status=400)
        
        try:
            age_min = int(age_min)
            age_max = int(age_max)
            if age_min > age_max:
                return JsonResponse({'error': 'Минимальный возраст не может быть больше максимального'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Возраст должен быть числом'}, status=400)
        
        if group_id:  # РЕДАКТИРОВАНИЕ
            try:
                group = BalletGroup.objects.get(id=group_id)
                group.name = name
                group.age_min = age_min
                group.age_max = age_max
                group.is_active = is_active
                
                # Назначаем преподавателя
                if teacher_id:
                    try:
                        teacher = User.objects.get(id=teacher_id)
                        group.teacher = teacher
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'Преподаватель не найден'}, status=400)
                else:
                    group.teacher = None
                
                group.save()
                print(f"✅ Группа '{name}' обновлена")
                
                return JsonResponse({'success': True, 'id': group.id})
                
            except BalletGroup.DoesNotExist:
                return JsonResponse({'error': 'Группа не найдена'}, status=404)
        
        else:  # СОЗДАНИЕ
            # Проверяем, нет ли уже группы с таким названием
            if BalletGroup.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Группа с таким названием уже существует'}, status=400)
            
            group = BalletGroup.objects.create(
                name=name,
                age_min=age_min,
                age_max=age_max,
                is_active=is_active
            )
            
            # Назначаем преподавателя
            if teacher_id:
                try:
                    teacher = User.objects.get(id=teacher_id)
                    group.teacher = teacher
                    group.save()
                except User.DoesNotExist:
                    pass
            
            print(f"✅ Новая группа создана: '{name}'")
            return JsonResponse({'success': True, 'id': group.id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)
    

@csrf_exempt
@login_required
@staff_member_required
def api_delete_group(request):
    """Удаление группы"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST метод разрешен'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        group_id = data.get('group_id')
        
        group = BalletGroup.objects.get(id=group_id)
        
        # Проверяем, есть ли связанные записи
        if group.schedules.exists():
            return JsonResponse({'error': 'Нельзя удалить группу, в которой есть занятия'}, status=400)
        
        if group.students.exists():
            return JsonResponse({'error': 'Нельзя удалить группу, в которой есть ученики'}, status=400)
        
        group_name = group.name
        group.delete()
        print(f"🗑️ Группа удалена: {group_name}")
        
        return JsonResponse({'success': True})
        
    except BalletGroup.DoesNotExist:
        return JsonResponse({'error': 'Группа не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@staff_member_required
def api_get_group_students(request, group_id):
    """Получение списка учеников в группе"""
    try:
        group = BalletGroup.objects.get(id=group_id)
        
        # Получаем всех учеников, у которых в профиле указана эта группа
        students = User.objects.filter(
            groups__name='Студенты',
            student_profile__group=group
        ).select_related('student_profile').order_by('last_name', 'first_name')
        
        students_data = []
        for student in students:
            profile = student.student_profile
            students_data.append({
                'id': student.id,
                'username': student.username,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': profile.phone if profile else '',
                'age': profile.age if profile else None,
                'is_active': student.is_active,
                'date_joined': student.date_joined.strftime('%d.%m.%Y')
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data
        })
        
    except BalletGroup.DoesNotExist:
        return JsonResponse({'error': 'Группа не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@staff_member_required
def api_get_student_details(request, student_id):
    """Получение детальной информации об ученике"""
    try:
        student = User.objects.get(id=student_id, groups__name='Студенты')
        profile = student.student_profile if hasattr(student, 'student_profile') else None
        
        # Получаем историю записей ученика
        bookings = Booking.objects.filter(
            schedule__group__students=student
        ).select_related('schedule', 'schedule__group').order_by('-created_at')[:10]
        
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'date': booking.schedule.date.strftime('%d.%m.%Y'),
                'time': booking.schedule.start_time.strftime('%H:%M'),
                'group': booking.schedule.group.name,
                'status': booking.status,
                'created_at': booking.created_at.strftime('%d.%m.%Y %H:%M')
            })
        
        data = {
            'id': student.id,
            'username': student.username,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'phone': profile.phone if profile else '',
            'age': profile.age if profile else None,
            'is_active': student.is_active,
            'date_joined': student.date_joined.strftime('%d.%m.%Y'),
            'bookings': bookings_data
        }
        
        return JsonResponse({'success': True, 'student': data})
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Ученик не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ========== API ДЛЯ РАСПИСАНИЯ ==========

@csrf_exempt
@login_required
@staff_member_required
def api_add_schedule(request):
    """Добавление нового времени занятия"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        date_str = data.get('date')
        group_id = data.get('group_id')
        time_str = data.get('time')
        is_trial = data.get('is_trial', False)
        max_seats = data.get('max_seats', 10)
        
        if not date_str or not group_id or not time_str:
            return JsonResponse({'error': 'Не все поля заполнены'}, status=400)
        
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Проверяем, нет ли уже такого занятия
        existing = Schedule.objects.filter(
            group_id=group_id,
            date=date_obj,
            start_time=time_obj
        ).first()
        
        if existing:
            return JsonResponse({'error': 'Такое занятие уже существует'}, status=400)
        
        schedule = Schedule.objects.create(
            group_id=group_id,
            date=date_obj,
            start_time=time_obj,
            duration=60,
            max_seats=max_seats,
            is_trial=is_trial,
            is_active=True
        )
        
        return JsonResponse({'success': True, 'id': schedule.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@staff_member_required
def api_get_schedule_bookings(request, schedule_id):
    """Получение списка записей на занятие и доступных учеников"""
    try:
        schedule = Schedule.objects.select_related('group').get(id=schedule_id)
        group = schedule.group
        
        # Текущие записи
        bookings = Booking.objects.filter(schedule=schedule).order_by('full_name')
        bookings_data = [{
            'id': b.id,
            'full_name': b.full_name,
            'phone': b.phone,
            'child_name': b.child_name,
            'child_age': b.child_age
        } for b in bookings]
        
        # Ученики из этой группы
        students = User.objects.filter(
            groups__name='Студенты',
            student_profile__group=group,
            is_active=True
        ).select_related('student_profile')
        
        available_students = []
        for student in students:
            profile = student.student_profile if hasattr(student, 'student_profile') else None
            # Проверяем, не записан ли уже
            is_booked = Booking.objects.filter(
                schedule=schedule,
                full_name=student.get_full_name()
            ).exists()
            
            if not is_booked:
                available_students.append({
                    'id': student.id,
                    'full_name': f"{student.last_name} {student.first_name}".strip(),
                    'phone': profile.phone if profile else '',
                    'age': profile.age if profile and profile.age else None  # None если нет возраста
                })
        
        return JsonResponse({
            'success': True,
            'current_bookings': bookings_data,
            'available_students': available_students
        })
        
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Занятие не найдено'}, status=404)

@csrf_exempt
@login_required
@staff_member_required
def api_delete_schedule(request):
    """Удаление занятия"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        schedule_id = data.get('schedule_id')
        
        schedule = Schedule.objects.get(id=schedule_id)
        
        # Проверяем, есть ли записи
        if schedule.bookings.exists():
            return JsonResponse({'error': 'Нельзя удалить занятие с записями'}, status=400)
        
        schedule.delete()
        return JsonResponse({'success': True})
        
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Занятие не найдено'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_delete_day(request):
    """Удаление всех занятий за день"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        date_str = data.get('date')
        
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        schedules = Schedule.objects.filter(date=date_obj)
        
        # Проверяем, есть ли записи
        for schedule in schedules:
            if schedule.bookings.exists():
                return JsonResponse({'error': 'Нельзя удалить день с занятиями, на которые есть записи'}, status=400)
        
        count = schedules.delete()[0]
        return JsonResponse({'success': True, 'deleted': count})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_add_booking_to_schedule(request):
    """Добавление ученика на занятие"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        schedule_id = data.get('schedule_id')
        student_id = data.get('student_id')
        child_age = data.get('child_age', 0)
        phone = data.get('phone', '')
        
        schedule = Schedule.objects.get(id=schedule_id)
        student = User.objects.get(id=student_id)
        
        # Проверяем места
        if schedule.get_free_seats() <= 0:
            return JsonResponse({'error': 'Нет свободных мест'}, status=400)
        
        # Создаем запись
        booking = Booking.objects.create(
            schedule=schedule,
            full_name=student.get_full_name(),
            phone=phone,
            child_name='',
            child_age=child_age,
            status='confirmed'
        )
        
        schedule.booked_seats += 1
        schedule.save()
        
        return JsonResponse({'success': True, 'booking_id': booking.id})
        
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Занятие не найдено'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Ученик не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@staff_member_required
def api_get_day_schedules(request, date_str):
    """Получение всех занятий за конкретный день для редактирования"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        schedules = Schedule.objects.filter(
            date=date_obj
        ).select_related('group').order_by('group__name', 'start_time')
        
        schedules_data = []
        for s in schedules:
            schedules_data.append({
                'id': s.id,
                'group_id': s.group.id,
                'time': s.start_time.strftime('%H:%M'),
                'is_trial': s.is_trial,
                'max_seats': s.max_seats
            })
        
        return JsonResponse({'success': True, 'schedules': schedules_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_batch_save_schedules(request):
    """Пакетное сохранение занятий за день"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        date_str = data.get('date')
        slots = data.get('slots', [])
        
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Получаем ID существующих занятий из слотов
        existing_ids = []
        for slot in slots:
            if slot.get('schedule_id'):
                existing_ids.append(int(slot['schedule_id']))
        
        # Удаляем занятия, которых нет в списке
        Schedule.objects.filter(date=date_obj).exclude(id__in=existing_ids).delete()
        
        # Обновляем или создаем занятия
        for slot in slots:
            schedule_id = slot.get('schedule_id')
            group_id = slot.get('group_id')
            time_str = slot.get('time')
            is_trial = slot.get('is_trial', False)
            max_seats = slot.get('max_seats', 10)
            
            if not group_id or not time_str:
                continue
            
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            
            if schedule_id:
                # Обновляем существующее
                schedule = Schedule.objects.get(id=schedule_id)
                schedule.group_id = group_id
                schedule.start_time = time_obj
                schedule.is_trial = is_trial
                schedule.max_seats = max_seats
                schedule.save()
            else:
                # Создаем новое
                Schedule.objects.create(
                    group_id=group_id,
                    date=date_obj,
                    start_time=time_obj,
                    duration=60,
                    max_seats=max_seats,
                    is_trial=is_trial,
                    is_active=True
                )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_toggle_trial(request):
    """Переключение типа занятия (обычное/пробное)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        schedule_id = data.get('schedule_id')
        is_trial = data.get('is_trial')
        
        schedule = Schedule.objects.get(id=schedule_id)
        schedule.is_trial = is_trial
        schedule.save()
        
        return JsonResponse({'success': True})
        
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Занятие не найдено'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@staff_member_required
def api_remove_booking(request):
    """Удаление записи с занятия"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        booking_id = data.get('booking_id')
        
        print(f"🗑️ Удаление записи ID: {booking_id}")
        
        booking = Booking.objects.get(id=booking_id)
        schedule = booking.schedule
        
        # Удаляем запись
        booking.delete()
        
        # Уменьшаем счетчик занятых мест
        schedule.booked_seats -= 1
        schedule.save()
        
        print(f"✅ Запись удалена, свободных мест: {schedule.get_free_seats()}")
        
        return JsonResponse({'success': True})
        
    except Booking.DoesNotExist:
        print(f"❌ Запись {booking_id} не найдена")
        return JsonResponse({'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)