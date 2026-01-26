let selectedSchedule = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, загружаем группы...');

    fetch('/api/groups/')
        .then(response => {
            console.log('Ответ от /api/groups/:', response.status);
            if (!response.ok) {
                throw new Error('Ошибка загрузки групп: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Данные групп получены:', data);
            const select = document.getElementById('groupSelect');

            if (!select) {
                console.error('Элемент groupSelect не найден!');
                return;
            }

            select.innerHTML = '<option value="">Выберите группу для обучения</option>';

            if (data.groups && Array.isArray(data.groups)) {
                data.groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group.id;
                    option.textContent = group.name;
                    select.appendChild(option);
                });
                console.log(`Загружено ${data.groups.length} групп`);
            } else {
                console.error('Некорректный формат данных групп:', data);
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке групп:', error);
        });
});

function loadSchedule(groupId) {
    console.log('loadSchedule вызвана с groupId:', groupId);

    const scheduleContainer = document.getElementById('scheduleContainer');
    const selectedInfo = document.getElementById('selectedInfo');
    const scheduleItems = document.getElementById('scheduleItems');

    if (!groupId) {
        console.log('groupId не выбран, скрываем расписание');
        if (scheduleContainer) scheduleContainer.style.display = 'none';
        if (selectedInfo) selectedInfo.style.display = 'none';
        selectedSchedule = null;
        return;
    }

    const apiUrl = `/api/schedule/?group_id=${groupId}`;
    console.log('Запрашиваем API:', apiUrl);

    fetch(apiUrl)
        .then(response => {
            console.log('Ответ получен, статус:', response.status, response.statusText);

            if (response.status === 404) {
                throw new Error('API не найден. Проверьте URL.');
            }
            if (response.status === 500) {
                throw new Error('Ошибка сервера. Попробуйте позже.');
            }
            if (!response.ok) {
                throw new Error('Ошибка сети: ' + response.status);
            }

            return response.json().then(data => {
                if (!data) {
                    throw new Error('Пустой ответ от сервера');
                }
                return data;
            });
        })
        .then(data => {
            console.log('Данные расписания получены:', data);

            if (!scheduleItems) {
                console.error('Элемент scheduleItems не найден!');
                return;
            }

            scheduleItems.innerHTML = '';

            if (!data.schedule || data.schedule.length === 0) {
                console.log('Нет доступных занятий');
                scheduleItems.innerHTML = '<p style="color: #666; padding: 10px;">Нет доступных занятий на ближайшее время</p>';
            } else {
                console.log(`Найдено занятий: ${data.schedule.length}`);

                // Группируем занятия по датам
                const dates = {};
                data.schedule.forEach(item => {
                    if (item && item.date) {
                        if (!dates[item.date]) dates[item.date] = [];
                        dates[item.date].push(item);
                    }
                });

                console.log('Сгруппированные даты:', Object.keys(dates));

                // Сортируем даты по возрастанию
                const sortedDates = Object.keys(dates).sort();

                // Создаем блоки для каждой даты
                sortedDates.forEach(dateStr => {
                    const date = new Date(dateStr);
                    const times = dates[dateStr];

                    const dateBlock = document.createElement('div');
                    dateBlock.className = 'date-block';
                    dateBlock.innerHTML = `<h6>${date.getDate()} февраля (суббота):</h6>`;

                    const timeContainer = document.createElement('div');
                    timeContainer.className = 'time-container';

                    times.forEach(slot => {
                        const timeBtn = document.createElement('button');
                        timeBtn.type = 'button'; // Важно для предотвращения отправки формы
                        timeBtn.className = 'time-btn';
                        timeBtn.innerHTML = `${slot.time} (${slot.free_seats || 0} свободно)`;
                        timeBtn.onclick = () => {
                            console.log('Выбрано время:', slot);
                            selectTime(slot, date);
                        };

                        if (slot.free_seats === 0) {
                            timeBtn.disabled = true;
                            timeBtn.classList.add('disabled');
                            timeBtn.title = 'Мест нет';
                        }

                        timeContainer.appendChild(timeBtn);
                    });

                    dateBlock.appendChild(timeContainer);
                    scheduleItems.appendChild(dateBlock);
                });
            }

            if (scheduleContainer) {
                scheduleContainer.style.display = 'block';
                console.log('Расписание отображено');
            }

            if (selectedInfo) {
                selectedInfo.style.display = 'none';
            }

            selectedSchedule = null;
        })
        .catch(error => {
            console.error('Ошибка при загрузке расписания:', error);

            if (scheduleItems) {
                scheduleItems.innerHTML = `
                    <div style="color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <strong>Ошибка загрузки расписания:</strong><br>
                        ${error.message}<br>
                        <small>Проверьте подключение к интернету и попробуйте снова</small>
                    </div>
                `;
            }

            if (scheduleContainer) {
                scheduleContainer.style.display = 'block';
            }
        });
}

function selectTime(schedule, date) {
    console.log('Выбрано время занятия:', schedule);
    selectedSchedule = schedule;

    const selectedInfo = document.getElementById('selectedInfo');
    if (selectedInfo) {
        selectedInfo.innerHTML = `
            <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                <strong>✅ Вы выбрали:</strong><br>
                ${date.getDate()} февраля, ${schedule.time}<br>
                <small style="color: #666;">Нажмите "Записаться" для подтверждения</small>
            </div>
        `;
        selectedInfo.style.display = 'block';
    }
}

function submitBooking() {
    console.log('Начало отправки записи...');

    if (!selectedSchedule) {
        alert('Пожалуйста, выберите время занятия');
        return;
    }

    const fullName = document.getElementById('fullName').value.trim();
    const phone = document.getElementById('phone').value.trim();

    if (!fullName) {
        alert('Введите ваше ФИО');
        document.getElementById('fullName').focus();
        return;
    }

    if (!phone || phone.length < 10) {
        alert('Введите корректный номер телефона');
        document.getElementById('phone').focus();
        return;
    }

    const bookingData = {
        schedule_id: selectedSchedule.id,
        full_name: fullName,
        phone: phone,
        child_name: '',
        child_age: 0,
        notes: ''
    };

    console.log('Отправляем данные:', bookingData);

    fetch('/api/booking/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(bookingData)
        })
        .then(response => {
            console.log('Ответ от сервера:', response.status);
            return response.json().then(data => {
                return { status: response.status, data: data };
            });
        })
        .then(result => {
            console.log('Результат:', result);

            if (result.status === 201 || result.status === 200) {
                if (result.data.success) {
                    alert(`✅ Запись #${result.data.booking_id} успешно создана!\n\nАдминистратор свяжется с вами в ближайшее время.`);
                    resetForm();
                } else {
                    alert('Ошибка: ' + (result.data.error || 'Неизвестная ошибка'));
                }
            } else {
                alert(`Ошибка сервера (${result.status}): ${result.data.error || 'Попробуйте позже'}`);
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке:', error);
            alert('Ошибка при отправке формы. Проверьте подключение к интернету.');
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function resetForm() {
    console.log('Сброс формы...');

    document.getElementById('fullName').value = '';
    document.getElementById('phone').value = '';

    const groupSelect = document.getElementById('groupSelect');
    if (groupSelect) groupSelect.value = '';

    const scheduleContainer = document.getElementById('scheduleContainer');
    if (scheduleContainer) scheduleContainer.style.display = 'none';

    const selectedInfo = document.getElementById('selectedInfo');
    if (selectedInfo) selectedInfo.style.display = 'none';

    const scheduleItems = document.getElementById('scheduleItems');
    if (scheduleItems) scheduleItems.innerHTML = '';

    selectedSchedule = null;

    console.log('Форма сброшена');
}

// Добавляем обработчик для кнопки "Записаться" чтобы предотвратить стандартное поведение ссылки
document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Предотвращаем переход по ссылке
            submitBooking();
        });
    }
});