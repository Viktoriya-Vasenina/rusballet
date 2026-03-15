import logging
import re
import time
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from telegram.request import HTTPXRequest
from rusballet_app.models import Group, Schedule, Booking

# Состояния для разговора (запись)
NAME, PHONE, CHILD_NAME, CHILD_AGE, CONFIRM = range(5)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Бот для записи на пробные занятия'
    
    def handle(self, *args, **options):
        """Запуск бота с автоматическим переподключением"""
        if not settings.BOT_TOKEN:
            self.stdout.write(self.style.ERROR('❌ Токен не найден!'))
            return
        
        self.stdout.write(self.style.SUCCESS('🚀 Запуск бота...'))
        
        # Бесконечный цикл для автоматического переподключения при ошибках
        while True:
            try:
                # Настраиваем HTTP клиент с увеличенными таймаутами
                request = HTTPXRequest(
                    connect_timeout=30.0,
                    read_timeout=30.0,
                    write_timeout=30.0,
                    pool_timeout=30.0
                )
                
                # Создаем приложение
                application = (
                    Application.builder()
                    .token(settings.BOT_TOKEN)
                    .request(request)
                    .build()
                )
                
                # Команда /start
                application.add_handler(CommandHandler("start", self.start_command))
                
                # Обработчик текстовых сообщений для сбора данных
                application.add_handler(MessageHandler(
                    filters.TEXT & ~filters.COMMAND, 
                    self.handle_message
                ))
                
                # Обработчики кнопок
                application.add_handler(CallbackQueryHandler(
                    self.button_handler, 
                    pattern="^(trial|channel|back_to_main|group_|schedule_|confirm|cancel)$"
                ))
                
                self.stdout.write(self.style.SUCCESS('✅ Бот запущен и готов к работе!'))
                
                # Запускаем с параметрами для надежности
                application.run_polling(
                    drop_pending_updates=True,
                    allowed_updates=Update.ALL_TYPES,
                    close_loop=False  # Важно для повторного подключения!
                )
                
            except Exception as e:
                logger.error(f"❌ Ошибка в работе бота: {e}")
                self.stdout.write(self.style.WARNING(f'⏱️ Ошибка: {e}. Переподключение через 5 секунд...'))
                time.sleep(5)
                continue  # Пробуем снова
    
    # ========== РАБОТА С БД ==========
    
    @sync_to_async
    def get_active_groups(self):
        """Получить все активные группы"""
        return list(Group.objects.filter(is_active=True))
    
    @sync_to_async
    def get_group_by_id(self, group_id):
        """Получить группу по ID"""
        return Group.objects.get(id=group_id)
    
    @sync_to_async
    def get_schedules_for_group(self, group_id):
        """Получить расписание для группы на ближайшие 14 дней"""
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        schedules = Schedule.objects.filter(
            group_id=group_id,
            date__gte=start_date,
            date__lte=end_date,
            is_active=True,
            is_trial=True  # Только пробные занятия
        ).order_by('date', 'start_time')
        
        return list(schedules)
    
    @sync_to_async
    def get_schedule_by_id(self, schedule_id):
        """Получить занятие по ID"""
        try:
            return Schedule.objects.select_related('group').get(id=schedule_id, is_active=True)
        except Schedule.DoesNotExist:
            return None
    
    @sync_to_async
    def create_booking(self, schedule_id, user_data):
        """Создать запись в БД"""
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            
            # Проверяем наличие мест
            if schedule.get_free_seats() <= 0:
                return None, "Нет свободных мест"
            
            # Создаем запись
            booking = Booking.objects.create(
                schedule=schedule,
                full_name=user_data['full_name'],
                phone=user_data['phone'],
                child_name=user_data['child_name'],
                child_age=int(user_data['child_age']),
                notes="Запись через Telegram",
                status='confirmed'
            )
            
            # Увеличиваем счетчик занятых мест
            schedule.booked_seats += 1
            schedule.save()
            
            return booking, None
            
        except Exception as e:
            logger.error(f"Ошибка при создании записи: {e}")
            return None, str(e)
    
    # ========== ОБРАБОТЧИКИ ==========
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню с двумя кнопками"""
        keyboard = [
            [InlineKeyboardButton("📝 Записаться на пробное занятие", callback_data="trial")],
            [InlineKeyboardButton("📢 Основной канал", callback_data="channel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🩰 Добро пожаловать в школу балета!\n\nВыберите действие:",
            reply_markup=reply_markup
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех кнопок"""
        query = update.callback_query
        await query.answer()
        
        # Главное меню
        if query.data == "trial":
            await self.show_groups(query)
        elif query.data == "channel":
            await query.edit_message_text(
                "📢 Здесь будет ссылка на основной канал\n\nСкоро появится!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="back_to_main")
                ]])
            )
        elif query.data == "back_to_main":
            await self.back_to_main(query)
        
        # Выбор группы
        elif query.data.startswith("group_"):
            group_id = int(query.data.replace("group_", ""))
            await self.show_schedule(query, group_id)
        
        # Выбор времени
        elif query.data.startswith("schedule_"):
            schedule_id = int(query.data.replace("schedule_", ""))
            await self.start_booking(query, context, schedule_id)
        
        # Подтверждение записи
        elif query.data == "confirm":
            await self.confirm_booking(query, context)
        elif query.data == "cancel":
            await self.cancel_booking(query, context)
    
    async def show_groups(self, query):
        """Показать список групп"""
        groups = await self.get_active_groups()
        
        if not groups:
            await query.edit_message_text(
                "😔 Нет доступных групп.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="back_to_main")
                ]])
            )
            return
        
        keyboard = []
        for group in groups:
            btn_text = f"{group.name} ({group.age_min}-{group.age_max} лет)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"group_{group.id}")])
        
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="back_to_main")])
        
        await query.edit_message_text(
            "📚 Выберите группу:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_schedule(self, query, group_id):
        """Показать расписание для группы"""
        schedules = await self.get_schedules_for_group(group_id)
        
        if not schedules:
            await query.edit_message_text(
                "😔 Нет занятий на ближайшие 2 недели.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« К группам", callback_data="trial")
                ]])
            )
            return
        
        group = await self.get_group_by_id(group_id)
        
        keyboard = []
        for s in schedules:
            free = s.get_free_seats()
            if free > 0:
                btn_text = f"{s.date.strftime('%d.%m')} {s.start_time.strftime('%H:%M')} - {free} мест"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"schedule_{s.id}")])
        
        if not keyboard:
            await query.edit_message_text(
                "😔 Нет свободных мест.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« К группам", callback_data="trial")
                ]])
            )
            return
        
        keyboard.append([InlineKeyboardButton("« К группам", callback_data="trial")])
        
        await query.edit_message_text(
            f"📅 {group.name}\n\nВыберите время:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def start_booking(self, query, context, schedule_id):
        """Начало процесса записи"""
        schedule = await self.get_schedule_by_id(schedule_id)
        
        if not schedule:
            await query.edit_message_text(
                "❌ Занятие недоступно.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« К группам", callback_data="trial")
                ]])
            )
            return ConversationHandler.END
        
        context.user_data['schedule_id'] = schedule_id
        context.user_data['schedule_info'] = {
            'group': schedule.group.name,
            'date': schedule.date.strftime('%d.%m.%Y'),
            'time': schedule.start_time.strftime('%H:%M')
        }
        
        await query.edit_message_text(
            f"📝 Запись на занятие\n"
            f"Группа: {schedule.group.name}\n"
            f"Дата: {schedule.date.strftime('%d.%m.%Y')}\n"
            f"Время: {schedule.start_time.strftime('%H:%M')}\n\n"
            f"Шаг 1 из 4: Введите ваше ФИО:"
        )
        
        return NAME
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений для сбора данных"""
        # Получаем текущее состояние из user_data
        # Так как мы не используем ConversationHandler, нужно отслеживать состояние вручную
        
        if 'schedule_id' not in context.user_data:
            await update.message.reply_text(
                "Пожалуйста, начните с команды /start"
            )
            return
        
        if 'step' not in context.user_data:
            context.user_data['step'] = NAME
        
        step = context.user_data['step']
        
        if step == NAME:
            await self.get_name(update, context)
        elif step == PHONE:
            await self.get_phone(update, context)
        elif step == CHILD_NAME:
            await self.get_child_name(update, context)
        elif step == CHILD_AGE:
            await self.get_child_age(update, context)
    
    async def get_name(self, update, context):
        """Получение ФИО"""
        name = update.message.text.strip()
        
        if len(name) < 3:
            await update.message.reply_text("❌ Слишком короткое имя. Введите ФИО полностью:")
            return
        
        context.user_data['full_name'] = name
        context.user_data['step'] = PHONE
        
        await update.message.reply_text(
            "✅ Спасибо!\n\n"
            "Шаг 2 из 4: Введите ваш телефон (например: +7 999 123-45-67):"
        )
    
    async def get_phone(self, update, context):
        """Получение телефона"""
        phone = update.message.text.strip()
        
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if len(phone_clean) < 10:
            await update.message.reply_text("❌ Некорректный номер. Введите снова (например: +7 999 123-45-67):")
            return
        
        context.user_data['phone'] = phone
        context.user_data['step'] = CHILD_NAME
        
        await update.message.reply_text(
            "✅ Номер принят!\n\n"
            "Шаг 3 из 4: Введите имя ребенка:"
        )
    
    async def get_child_name(self, update, context):
        """Получение имени ребенка"""
        child_name = update.message.text.strip()
        
        if len(child_name) < 2:
            await update.message.reply_text("❌ Слишком короткое имя. Введите имя ребенка:")
            return
        
        context.user_data['child_name'] = child_name
        context.user_data['step'] = CHILD_AGE
        
        await update.message.reply_text(
            "✅ Имя принято!\n\n"
            "Шаг 4 из 4: Введите возраст ребенка (число):"
        )
    
    async def get_child_age(self, update, context):
        """Получение возраста ребенка"""
        age_text = update.message.text.strip()
        
        try:
            age = int(age_text)
            if age < 1 or age > 18:
                await update.message.reply_text("❌ Возраст должен быть от 1 до 18 лет. Введите снова:")
                return
        except ValueError:
            await update.message.reply_text("❌ Введите число (возраст ребенка):")
            return
        
        context.user_data['child_age'] = age
        
        # Показываем подтверждение
        info = context.user_data.get('schedule_info', {})
        
        text = (
            f"📋 Проверьте данные:\n\n"
            f"🏛 Группа: {info.get('group')}\n"
            f"📅 Дата: {info.get('date')}\n"
            f"⏰ Время: {info.get('time')}\n\n"
            f"👤 ФИО: {context.user_data['full_name']}\n"
            f"📞 Телефон: {context.user_data['phone']}\n"
            f"🧒 Ребенок: {context.user_data['child_name']}\n"
            f"🔢 Возраст: {context.user_data['child_age']}\n\n"
            f"Всё верно?"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Да, записаться", callback_data="confirm")],
            [InlineKeyboardButton("❌ Нет, отмена", callback_data="cancel")]
        ]
        
        # Отправляем клавиатуру для подтверждения
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def confirm_booking(self, query, context):
        """Подтверждение записи"""
        schedule_id = context.user_data.get('schedule_id')
        
        if not schedule_id:
            await query.edit_message_text(
                "❌ Ошибка. Начните заново.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="back_to_main")
                ]])
            )
            context.user_data.clear()
            return
        
        booking, error = await self.create_booking(schedule_id, context.user_data)
        
        if booking:
            info = context.user_data.get('schedule_info', {})
            await query.edit_message_text(
                f"✅ Запись создана!\n\n"
                f"Группа: {info.get('group')}\n"
                f"Дата: {info.get('date')}\n"
                f"Время: {info.get('time')}\n\n"
                f"Ждем вас! 🩰",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="back_to_main")
                ]])
            )
        else:
            await query.edit_message_text(
                f"❌ Ошибка: {error}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="back_to_main")
                ]])
            )
        
        context.user_data.clear()
    
    async def cancel_booking(self, query, context):
        """Отмена записи"""
        context.user_data.clear()
        await query.edit_message_text(
            "❌ Запись отменена.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« В главное меню", callback_data="back_to_main")
            ]])
        )
    
    async def back_to_main(self, query):
        """Возврат в главное меню"""
        keyboard = [
            [InlineKeyboardButton("📝 Записаться на пробное занятие", callback_data="trial")],
            [InlineKeyboardButton("📢 Основной канал", callback_data="channel")]
        ]
        
        await query.edit_message_text(
            "🩰 Главное меню\n\nВыберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )