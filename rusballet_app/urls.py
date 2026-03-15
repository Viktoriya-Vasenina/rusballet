from django.urls import path
from . import views

urlpatterns = [
    # Основные маршруты сайта
    path('', views.home, name='home'),
    path('api/groups/', views.api_groups, name='api_groups'),
    path('api/schedule/', views.api_schedule, name='api_schedule'),
    path('api/booking/create/', views.api_create_booking, name='api_create_booking'),
    path('telegram/bind/', views.telegram_bind, name='telegram_bind'),
    
    # Кастомная админка
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/login/', views.admin_login_view, name='admin_login'),
    path('dashboard/logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/teachers/', views.admin_teachers, name='admin_teachers'),
    path('dashboard/students/', views.admin_students, name='admin_students'),
    path('dashboard/schedule/', views.admin_schedule, name='admin_schedule'),
    path('dashboard/bookings/', views.admin_bookings, name='admin_bookings'),
    path('dashboard/trial-bookings/', views.admin_trial_bookings, name='admin_trial_bookings'),
    path('dashboard/groups/', views.admin_groups, name='admin_groups'),
    path('dashboard/group/<int:group_id>/', views.admin_group_detail, name='admin_group_detail'),
    
    # Маршруты для преподавателей
    path('dashboard/teacher/<int:teacher_id>/', views.admin_teacher_detail, name='admin_teacher_detail'),
    path('dashboard/teacher/<int:teacher_id>/groups/', views.admin_teacher_groups, name='admin_teacher_groups'),
    path('dashboard/teacher/<int:teacher_id>/schedule/', views.admin_teacher_schedule, name='admin_teacher_schedule'),
    
    # API для AJAX запросов (общие)
    path('dashboard/api/update-booking/', views.api_update_booking_status, name='api_update_booking'),
    path('dashboard/api/confirm-trial/', views.api_confirm_trial_booking, name='api_confirm_trial'),
    path('dashboard/api/cancel-trial/', views.api_cancel_trial_booking, name='api_cancel_trial'),
    
    # API для преподавателей
    path('dashboard/api/teacher/save/', views.api_save_teacher, name='api_save_teacher'),
    path('dashboard/api/teacher/status/', views.api_update_teacher_status, name='api_update_teacher_status'),

    # API для учеников
    path('dashboard/api/student/save/', views.api_save_student, name='api_save_student'),
    path('dashboard/api/student/status/', views.api_update_student_status, name='api_update_student_status'),
    path('dashboard/api/student/<int:student_id>/group/', views.api_get_student_group, name='api_get_student_group'),
    path('dashboard/api/student/<int:student_id>/details/', views.api_get_student_details, name='api_get_student_details'),
    
    # API для групп
    path('dashboard/api/group/save/', views.api_save_group, name='api_save_group'),
    path('dashboard/api/group/delete/', views.api_delete_group, name='api_delete_group'),
    path('dashboard/api/group/<int:group_id>/students/', views.api_get_group_students, name='api_get_group_students'),
    
    # API для расписания
    path('dashboard/api/schedule/add/', views.api_add_schedule, name='api_add_schedule'),
    path('dashboard/api/schedule/day/<str:date>/', views.api_get_day_schedules, name='api_get_day_schedules'),
    path('dashboard/api/schedule/batch-save/', views.api_batch_save_schedules, name='api_batch_save_schedules'),
    path('dashboard/api/schedule/<int:schedule_id>/bookings/', views.api_get_schedule_bookings, name='api_get_schedule_bookings'),
    path('dashboard/api/schedule/booking/add/', views.api_add_booking_to_schedule, name='api_add_booking'),
    path('dashboard/api/schedule/toggle-trial/', views.api_toggle_trial, name='api_toggle_trial'),
    path('dashboard/api/schedule/delete/', views.api_delete_schedule, name='api_delete_schedule'),
    path('dashboard/api/schedule/day/delete/', views.api_delete_day, name='api_delete_day'),
    path('dashboard/api/booking/delete/', views.api_remove_booking, name='api_remove_booking'), 
]