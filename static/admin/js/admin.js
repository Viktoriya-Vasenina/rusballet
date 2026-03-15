console.log("✅ admin.js загружен");

// Функция для получения CSRF токена
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

$(document).ready(function() {
    console.log("✅ jQuery готов, текущий URL:", window.location.pathname);

    // ===== ОБЩИЕ ФУНКЦИИ =====

    // Toggle меню
    $('#menuToggle').click(function() {
        $('.sidebar').toggleClass('active');
    });

    // Подсветка активного пункта меню
    let currentUrl = window.location.pathname;
    $('.sidebar-nav ul li a').each(function() {
        if ($(this).attr('href') === currentUrl) {
            $(this).parent().addClass('active');
        }
    });

    // Закрытие модальных окон по клику на фон
    $(window).click(function(event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').removeClass('active');
        }
    });

    // ===== ПРЕПОДАВАТЕЛИ =====
    // Эти обработчики работают на всех страницах, но сработают только если есть соответствующие элементы
    initTeachersHandlers();

    // ===== УЧЕНИКИ =====
    initStudentsHandlers();
});

// ===== ОБРАБОТЧИКИ ДЛЯ ПРЕПОДАВАТЕЛЕЙ =====
function initTeachersHandlers() {
    // Поиск по таблице преподавателей
    $('#searchInput').on('keyup', function() {
        let searchText = $(this).val().toLowerCase();
        $('#teachersTable tbody tr').each(function() {
            let text = $(this).text().toLowerCase();
            $(this).toggle(text.includes(searchText));
        });
    });

    // Фильтр по статусу для преподавателей
    $('#statusFilter').on('change', function() {
        let status = $(this).val();
        $('#teachersTable tbody tr').each(function() {
            if (!status || $(this).data('status') === status) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Выбрать всех
    $('#selectAll').on('change', function() {
        $('.select-item').prop('checked', $(this).prop('checked'));
    });

    // Массовые действия
    $('#bulkAction').on('change', function() {
        let action = $(this).val();
        if (!action) return;

        let selectedIds = [];
        $('.select-item:checked').each(function() {
            selectedIds.push($(this).data('id'));
        });

        if (selectedIds.length === 0) {
            showNotification('Выберите записи', 'warning');
            $(this).val('');
            return;
        }

        if (action === 'active' || action === 'inactive') {
            let isActive = (action === 'active');
            updateTeachersStatus(selectedIds, isActive);
        }

        $(this).val('');
    });

    // Кнопка добавления преподавателя
    $('#addTeacherBtn, #emptyAddBtn').click(function() {
        openTeacherModal();
    });

    // Кнопки редактирования преподавателя
    $('.edit-btn').click(function() {
        let id = $(this).data('id');
        let firstName = $(this).data('firstname');
        let lastName = $(this).data('lastname');
        let email = $(this).data('email');
        let username = $(this).data('username');
        let status = $(this).data('status');

        openTeacherModal(id, firstName, lastName, email, username, status);
    });

    // Закрытие модального окна преподавателя
    $('.modal-close').click(function() {
        $('#teacherModal').removeClass('active');
    });
}

function openTeacherModal(id, firstName, lastName, email, username, status) {
    if (id) {
        $('#modalTitle').text('Редактировать преподавателя');
        $('#teacherId').val(id);
        $('#username').val(username);
        $('#firstName').val(firstName);
        $('#lastName').val(lastName);
        $('#email').val(email);
        $('#password').val('');
        $('#password').prop('required', false);
        $('#passwordRequired').hide();
        $('#passwordHelp').text('Оставьте пустым, чтобы не менять');
        $('#status').val(status);
    } else {
        $('#modalTitle').text('Добавить преподавателя');
        $('#teacherId').val('');
        $('#username').val('');
        $('#firstName').val('');
        $('#lastName').val('');
        $('#email').val('');
        $('#password').val('');
        $('#password').prop('required', true);
        $('#passwordRequired').show();
        $('#passwordHelp').text('Минимум 8 символов');
        $('#status').val('active');
        $('#teacherGroup').val('');
    }
    $('#teacherModal').addClass('active');
}

window.closeModal = function() {
    $('#teacherModal').removeClass('active');
};

window.saveTeacher = function() {
    let data = {
        teacher_id: $('#teacherId').val(),
        username: $('#username').val().trim(),
        first_name: $('#firstName').val().trim(),
        last_name: $('#lastName').val().trim(),
        email: $('#email').val().trim(),
        password: $('#password').val(),
        is_active: $('#status').val(),
        group_id: $('#teacherGroup').val()
    };

    if (!data.username || !data.first_name || !data.last_name) {
        showNotification('Заполните имя, фамилию и логин', 'warning');
        return;
    }

    if (!data.teacher_id && !data.password) {
        showNotification('Введите пароль для нового преподавателя', 'warning');
        return;
    }

    let saveBtn = $('.modal-footer .btn-primary');
    let originalText = saveBtn.text();
    saveBtn.text('⏳ Сохранение...').prop('disabled', true);

    $.ajax({
        url: '/dashboard/api/teacher/save/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(data),
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                showNotification('✅ Преподаватель сохранен', 'success');
                closeModal();
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + response.error, 'error');
                saveBtn.text(originalText).prop('disabled', false);
            }
        },
        error: function() {
            showNotification('❌ Ошибка соединения', 'error');
            saveBtn.text(originalText).prop('disabled', false);
        }
    });
};

function updateTeachersStatus(ids, isActive) {
    $.ajax({
        url: '/dashboard/api/teacher/status/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: JSON.stringify({
            teacher_ids: ids,
            is_active: isActive
        }),
        contentType: 'application/json',
        success: function(response) {
            if (response.success) {
                showNotification(`✅ Статус обновлен для ${response.count} преподавателей`, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + response.error, 'error');
            }
        },
        error: function() {
            showNotification('❌ Ошибка соединения', 'error');
        }
    });
}

// ===== ОБРАБОТЧИКИ ДЛЯ УЧЕНИКОВ =====
function initStudentsHandlers() {
    let searchTimeout;

    // Поиск с задержкой
    $('#searchInput').on('keyup', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterStudents();
        }, 300);
    });

    // Фильтры
    $('#statusFilter, #groupFilter').on('change', function() {
        filterStudents();
    });

    // Кнопка добавления ученика
    $('#addStudentBtn, #emptyAddBtn').click(function() {
        openStudentModal();
    });

    // Кнопки редактирования ученика
    $('.edit-btn').click(function() {
        let id = $(this).data('id');
        let firstName = $(this).data('firstname');
        let lastName = $(this).data('lastname');
        let email = $(this).data('email');
        let username = $(this).data('username');
        let status = $(this).data('status');

        loadStudentGroup(id, function(groupId) {
            openStudentModal(id, firstName, lastName, email, username, status, groupId);
        });
    });

    // Кнопки записей ученика
    $('.bookings-btn').click(function() {
        let id = $(this).data('id');
        window.location.href = '/dashboard/bookings/?student=' + id;
    });

    // Закрытие модального окна ученика
    $('.modal-close').click(function() {
        $('#studentModal').removeClass('active');
    });
}

function filterStudents() {
    let searchText = $('#searchInput').val().toLowerCase();
    let status = $('#statusFilter').val();
    let group = $('#groupFilter').val();

    $('#studentsTable tbody tr').each(function() {
        let show = true;
        let row = $(this);

        if (searchText) {
            let text = row.text().toLowerCase();
            if (!text.includes(searchText)) {
                show = false;
            }
        }

        if (show && status) {
            let rowStatus = row.data('status');
            if (rowStatus !== status) {
                show = false;
            }
        }

        if (show && group) {
            let rowGroup = row.data('group');
            if (rowGroup != group) {
                show = false;
            }
        }

        row.toggle(show);
    });
}

function loadStudentGroup(studentId, callback) {
    $.ajax({
        url: '/dashboard/api/student/' + studentId + '/group/',
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(response) {
            callback(response.group_id);
        },
        error: function() {
            callback('');
        }
    });
}

function openStudentModal(id, firstName, lastName, email, username, status, groupId) {
    if (id) {
        $('#modalTitle').text('Редактировать ученика');
        $('#studentId').val(id);
        $('#username').val(username);
        $('#firstName').val(firstName);
        $('#lastName').val(lastName);
        $('#email').val(email || '');
        $('#password').val('');
        $('#password').prop('required', false);
        $('#passwordRequired').hide();
        $('#passwordHelp').text('Оставьте пустым, чтобы не менять');
        $('#status').val(status || 'active');
        $('#studentGroup').val(groupId || '');
    } else {
        $('#modalTitle').text('Добавить ученика');
        $('#studentId').val('');
        $('#username').val('');
        $('#firstName').val('');
        $('#lastName').val('');
        $('#email').val('');
        $('#password').val('');
        $('#password').prop('required', true);
        $('#passwordRequired').show();
        $('#passwordHelp').text('Минимум 8 символов');
        $('#status').val('active');
        $('#studentGroup').val('');
    }
    $('#studentModal').addClass('active');
}

window.closeStudentModal = function() {
    $('#studentModal').removeClass('active');
};

window.saveStudent = function() {
    let data = {
        student_id: $('#studentId').val(),
        username: $('#username').val().trim(),
        first_name: $('#firstName').val().trim(),
        last_name: $('#lastName').val().trim(),
        email: $('#email').val().trim(),
        password: $('#password').val(),
        is_active: $('#status').val() === 'active',
        group_id: $('#studentGroup').val()
    };

    if (!data.username || !data.first_name || !data.last_name) {
        showNotification('Заполните имя, фамилию и логин', 'warning');
        return;
    }

    if (!data.student_id && !data.password) {
        showNotification('Введите пароль для нового ученика', 'warning');
        return;
    }

    let saveBtn = $('.modal-footer .btn-primary');
    let originalText = saveBtn.text();
    saveBtn.text('⏳ Сохранение...').prop('disabled', true);

    $.ajax({
        url: '/dashboard/api/student/save/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(data),
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                showNotification('✅ Ученик сохранен', 'success');
                closeStudentModal();
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + response.error, 'error');
                saveBtn.text(originalText).prop('disabled', false);
            }
        },
        error: function() {
            showNotification('❌ Ошибка соединения', 'error');
            saveBtn.text(originalText).prop('disabled', false);
        }
    });
};

function updateStudentsStatus(ids, isActive) {
    $.ajax({
        url: '/dashboard/api/student/status/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            student_ids: ids,
            is_active: isActive
        }),
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                showNotification(`✅ Статус обновлен для ${response.count} учеников`, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + response.error, 'error');
            }
        },
        error: function() {
            showNotification('❌ Ошибка соединения', 'error');
        }
    });
}

// ===== УВЕДОМЛЕНИЯ =====
function showNotification(message, type) {
    $('.notification').remove();

    let notification = $('<div class="notification ' + type + '">' + message + '</div>');
    $('body').append(notification);

    notification.fadeIn(300);

    setTimeout(function() {
        notification.fadeOut(300, function() {
            $(this).remove();
        });
    }, 3000);
}