@echo off
echo ========================================
echo УСТАНОВКА БИБЛИОТЕК ДЛЯ ROSUBLET
echo ========================================
echo.

echo [1/3] Проверка наличия pip...
where pip >nul 2>&1
if errorlevel 1 (
    echo ❌ pip не найден!
    echo Убедитесь, что Python установлен правильно
    pause
    exit /b
)
echo ✅ pip найден
echo.

echo [2/3] Установка библиотек из requirements.txt...
pip install -r requirements.txt
echo.

echo [3/3] Проверка установки...
python -c "import django; print(f'✅ Django {django.get_version()} установлен')"
python -c "import telegram; print(f'✅ python-telegram-bot установлен')"
echo.

echo ========================================
echo ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Теперь можно запускать проект:
echo   python manage.py runserver
echo   python manage.py runbot
echo.
pause