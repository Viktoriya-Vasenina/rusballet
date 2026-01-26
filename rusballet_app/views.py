from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
import json
from .models import Group, Schedule, Booking

def home(request):
    return render(request, 'home.html')

def api_groups(request):
    groups = Group.objects.filter(is_active=True)
    data = [{
        'id': g.id,
        'name': g.name,
        'age_range': f"{g.age_min}-{g.age_max} лет"
    } for g in groups]
    return JsonResponse({'groups': data})

def api_schedule(request):
    group_id = request.GET.get('group_id')
    
    if not group_id:
        return JsonResponse({'error': 'Укажите group_id'}, status=400)
    
    schedules = Schedule.objects.filter(
        group_id=group_id,
        is_active=True
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
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)