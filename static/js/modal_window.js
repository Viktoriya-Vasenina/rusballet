let selectedSchedule = null;
let isModal = false;

function setupTimeSlotStyles() {
    document.querySelectorAll('.time-slot').forEach(timeSlot => {
        timeSlot.addEventListener('mouseenter', function() {
            if (!this.classList.contains('selected')) {
                this.style.cursor = 'pointer';
                this.style.borderColor = '#4770FF';
                this.style.boxShadow = '0 0 0 2px rgba(71, 112, 255, 0.2)';
            }
        });

        timeSlot.addEventListener('mouseleave', function() {
            if (!this.classList.contains('selected')) {
                this.style.borderColor = '';
                this.style.boxShadow = '';
            }
        });

        timeSlot.addEventListener('click', function() {
            document.querySelectorAll('.time-slot').forEach(slot => {
                slot.classList.remove('selected');
                slot.style.borderColor = '';
                slot.style.boxShadow = '';
            });

            this.classList.add('selected');
            this.style.borderColor = '#339139';
            this.style.boxShadow = '0 0 0 2px rgba(51, 145, 57, 0.2)';
        });
    });
}

function resetModalForm() {
    selectedSchedule = null;

    const modalFullName = document.getElementById('modalFullName');
    const modalPhone = document.getElementById('modalPhone');
    const modalGroupSelect = document.getElementById('modalGroupSelect');
    const modalScheduleContainer = document.getElementById('modalScheduleContainer');

    if (modalFullName) modalFullName.value = '';
    if (modalPhone) modalPhone.value = '';
    if (modalGroupSelect) {
        modalGroupSelect.value = '';
        resetSelectStyles(modalGroupSelect);
    }

    if (modalScheduleContainer) {
        modalScheduleContainer.style.display = 'none';

        const existingDateBlocks = modalScheduleContainer.querySelectorAll('.schedule-date-block');
        existingDateBlocks.forEach(block => block.remove());

        const originalDateBlock = document.createElement('div');
        originalDateBlock.className = 'schedule-date-block';
        originalDateBlock.innerHTML = `
            <div class="date-header">07 февраля 2026 года</div>
            <div class="time-slots-container">
                <div class="time-slot">
                    <span class="time">10:00</span>
                    <span class="seats-info">свободно 4 из 5</span>
                </div>
                <div class="time-slot">
                    <span class="time">14:00</span>
                    <span class="seats-info">свободно 3 из 5</span>
                </div>
            </div>
        `;
        modalScheduleContainer.appendChild(originalDateBlock);
        setupTimeSlotStyles();
    }
}

function setupSelectStyles(selectElement) {
    if (!selectElement) return;

    selectElement.addEventListener('focus', function() {
        this.style.borderColor = '#4770FF';
        this.style.boxShadow = '0 0 0 2px rgba(71, 112, 255, 0.2)';
    });

    selectElement.addEventListener('blur', function() {
        if (this.value) {
            this.style.borderColor = '#339139';
            this.style.boxShadow = '0 0 0 2px rgba(51, 145, 57, 0.2)';
        } else {
            resetSelectStyles(this);
        }
    });

    selectElement.addEventListener('change', function() {
        if (this.value) {
            this.style.borderColor = '#339139';
            this.style.boxShadow = '0 0 0 2px rgba(51, 145, 57, 0.2)';
        } else {
            resetSelectStyles(this);
        }
    });
}

function resetSelectStyles(selectElement) {
    if (!selectElement) return;
    selectElement.style.borderColor = '';
    selectElement.style.boxShadow = '';
}

function lockBodyScroll() {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    if (scrollbarWidth > 0) {
        document.body.style.paddingRight = scrollbarWidth + 'px';
        const headerImg = document.querySelector('.header img');
        if (headerImg) {
            headerImg.dataset.originalMargin = headerImg.style.marginRight;
            const currentMargin = parseInt(window.getComputedStyle(headerImg).marginRight) || -55;
            headerImg.style.marginRight = (currentMargin - scrollbarWidth) + 'px';
        }
        const header = document.querySelector('.header');
        if (header) {
            header.dataset.originalPadding = header.style.paddingRight;
            const currentPadding = parseInt(window.getComputedStyle(header).paddingRight) || 0;
            header.style.paddingRight = (currentPadding + scrollbarWidth) + 'px';
        }
    }
    document.body.style.overflow = 'hidden';
}

function unlockBodyScroll() {
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    const headerImg = document.querySelector('.header img');
    if (headerImg && headerImg.dataset.originalMargin !== undefined) {
        headerImg.style.marginRight = headerImg.dataset.originalMargin;
        delete headerImg.dataset.originalMargin;
    }
    const header = document.querySelector('.header');
    if (header && header.dataset.originalPadding !== undefined) {
        header.style.paddingRight = header.dataset.originalPadding;
        delete header.dataset.originalPadding;
    }
}

function createModalFromExisting() {
    const originalRecord = document.querySelector('.record');
    if (!originalRecord) return null;
    originalRecord.style.display = 'none';
    const clonedRecord = originalRecord.cloneNode(true);
    clonedRecord.classList.add('modal-record');
    clonedRecord.style.display = 'block';

    const groupSelect = clonedRecord.querySelector('#groupSelect');
    if (groupSelect) {
        groupSelect.id = 'modalGroupSelect';
        groupSelect.onchange = function() {
            isModal = true;
            loadSchedule(this.value);
        };
        setupSelectStyles(groupSelect);
    }

    const scheduleContainer = clonedRecord.querySelector('#scheduleContainer');
    if (scheduleContainer) {
        scheduleContainer.id = 'modalScheduleContainer';
        scheduleContainer.style.display = 'none';
    }

    const fullName = clonedRecord.querySelector('#fullName');
    if (fullName) fullName.id = 'modalFullName';

    const phone = clonedRecord.querySelector('#phone');
    if (phone) phone.id = 'modalPhone';

    const submitBtn = clonedRecord.querySelector('#submitBtn');
    if (submitBtn) {
        submitBtn.id = 'modalSubmitBtn';
        submitBtn.onclick = function(e) {
            e.preventDefault();
            isModal = true;
            submitBooking();
        };
    }

    const modalContainer = document.createElement('div');
    modalContainer.id = 'modalContainer';
    modalContainer.className = 'modal-container';
    modalContainer.style.display = 'none';
    modalContainer.style.position = 'fixed';
    modalContainer.style.top = '0';
    modalContainer.style.left = '0';
    modalContainer.style.width = '100%';
    modalContainer.style.height = '100%';
    modalContainer.style.zIndex = '1000';

    const modalOverlay = document.createElement('div');
    modalOverlay.id = 'modalOverlay';
    modalOverlay.className = 'modal-overlay';
    modalOverlay.style.position = 'absolute';
    modalOverlay.style.top = '0';
    modalOverlay.style.left = '0';
    modalOverlay.style.width = '100%';
    modalOverlay.style.height = '100%';
    modalOverlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modalOverlay.style.cursor = 'pointer';

    const modalContent = document.createElement('div');
    modalContent.id = 'modalContent';
    modalContent.className = 'modal-content';
    modalContent.style.position = 'relative';
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '10px';
    modalContent.style.maxWidth = '500px';
    modalContent.style.width = '90%';
    modalContent.style.margin = 'auto';
    modalContent.style.marginTop = '50px';
    modalContent.style.marginBottom = '50px';
    modalContent.style.maxHeight = '85vh';
    modalContent.style.overflowY = 'auto';
    modalContent.style.boxShadow = '0 5px 15px rgba(0,0,0,0.3)';

    const closeBtn = document.createElement('button');
    closeBtn.id = 'modalClose';
    closeBtn.className = 'modal-close';
    closeBtn.innerHTML = '×';
    closeBtn.style.position = 'absolute';
    closeBtn.style.top = '10px';
    closeBtn.style.right = '15px';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.fontSize = '24px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.zIndex = '1002';

    modalContent.appendChild(closeBtn);
    modalContent.appendChild(clonedRecord);
    modalContainer.appendChild(modalOverlay);
    modalContainer.appendChild(modalContent);
    document.body.appendChild(modalContainer);

    return modalContainer;
}

function createPriseModal() {
    const originalPrise = document.querySelector('.prise');
    if (!originalPrise) return null;
    originalPrise.style.display = 'none';
    const clonedPrise = originalPrise.cloneNode(true);
    clonedPrise.classList.add('modal-prise');
    clonedPrise.style.display = 'block';

    const modalContainer = document.createElement('div');
    modalContainer.id = 'priseModalContainer';
    modalContainer.className = 'prise-modal-container';
    modalContainer.style.display = 'none';
    modalContainer.style.position = 'fixed';
    modalContainer.style.top = '0';
    modalContainer.style.left = '0';
    modalContainer.style.width = '100%';
    modalContainer.style.height = '100%';
    modalContainer.style.zIndex = '1000';

    const modalOverlay = document.createElement('div');
    modalOverlay.id = 'priseModalOverlay';
    modalOverlay.className = 'modal-overlay';
    modalOverlay.style.position = 'absolute';
    modalOverlay.style.top = '0';
    modalOverlay.style.left = '0';
    modalOverlay.style.width = '100%';
    modalOverlay.style.height = '100%';
    modalOverlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modalOverlay.style.cursor = 'pointer';

    const modalContent = document.createElement('div');
    modalContent.id = 'priseModalContent';
    modalContent.className = 'modal-content';
    modalContent.style.position = 'relative';
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '0 20px';
    modalContent.style.maxWidth = '1200px';
    modalContent.style.width = '90%';
    modalContent.style.margin = 'auto';
    modalContent.style.marginTop = '20px';
    modalContent.style.marginBottom = '20px';
    modalContent.style.boxShadow = '0 5px 15px rgba(0,0,0,0.3)';
    modalContent.style.maxHeight = '90vh';
    modalContent.style.overflowY = 'auto';

    const closeBtn = document.createElement('button');
    closeBtn.id = 'priseModalClose';
    closeBtn.className = 'modal-close';
    closeBtn.innerHTML = '×';
    closeBtn.style.position = 'absolute';
    closeBtn.style.top = '10px';
    closeBtn.style.right = '15px';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.fontSize = '24px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.zIndex = '1002';

    modalContent.appendChild(closeBtn);
    modalContent.appendChild(clonedPrise);
    modalContainer.appendChild(modalOverlay);
    modalContainer.appendChild(modalContent);
    document.body.appendChild(modalContainer);

    return modalContainer;
}

function openModal() {
    isModal = true;
    let modalContainer = document.getElementById('modalContainer');
    if (!modalContainer) {
        modalContainer = createModalFromExisting();
        if (!modalContainer) return;
    }

    const priseModalContainer = document.getElementById('priseModalContainer');
    if (priseModalContainer) {
        priseModalContainer.style.display = 'none';
    }

    modalContainer.style.display = 'block';
    lockBodyScroll();
    loadGroupsForModal();
}

function openPriseModal() {
    isModal = false;
    let modalContainer = document.getElementById('priseModalContainer');
    if (!modalContainer) {
        modalContainer = createPriseModal();
        if (!modalContainer) return;
    }

    const recordModalContainer = document.getElementById('modalContainer');
    if (recordModalContainer) {
        recordModalContainer.style.display = 'none';
    }

    modalContainer.style.display = 'block';
    lockBodyScroll();
}

function closeModal() {
    isModal = false;
    const modalContainer = document.getElementById('modalContainer');
    if (!modalContainer) return;
    modalContainer.style.display = 'none';
    unlockBodyScroll();
    resetModalForm();
}

function closePriseModal() {
    isModal = false;
    const modalContainer = document.getElementById('priseModalContainer');
    if (!modalContainer) return;
    modalContainer.style.display = 'none';
    unlockBodyScroll();
}

function loadGroupsForModal() {
    fetch('/api/groups/')
        .then(response => {
            if (!response.ok) throw new Error('Ошибка загрузки групп');
            return response.json();
        })
        .then(data => {
            const select = document.getElementById('modalGroupSelect');
            if (!select) return;

            select.innerHTML = '<option value="">Выберите возрастную группу</option>';

            if (data.groups && Array.isArray(data.groups)) {
                data.groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group.id;
                    option.textContent = group.name;
                    select.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке групп:', error);
        });
}

function loadSchedule(groupId) {
    if (!groupId) {
        if (isModal) {
            const scheduleContainer = document.getElementById('modalScheduleContainer');
            if (scheduleContainer) scheduleContainer.style.display = 'none';
        } else {
            const scheduleContainer = document.getElementById('scheduleContainer');
            if (scheduleContainer) scheduleContainer.style.display = 'none';
        }
        selectedSchedule = null;
        return;
    }

    let scheduleContainer;

    if (isModal) {
        scheduleContainer = document.getElementById('modalScheduleContainer');
    } else {
        scheduleContainer = document.getElementById('scheduleContainer');
    }

    if (!scheduleContainer) return;

    scheduleContainer.style.display = 'block';

    const existingDateBlocks = scheduleContainer.querySelectorAll('.schedule-date-block');
    existingDateBlocks.forEach(block => block.remove());

    const loadingBlock = document.createElement('div');
    loadingBlock.className = 'schedule-date-block';
    loadingBlock.innerHTML = '<div class="date-header">Загрузка...</div><div class="time-slots-container"></div>';
    scheduleContainer.appendChild(loadingBlock);

    fetch(`/api/schedule/?group_id=${groupId}`)
        .then(response => {
            if (!response.ok) throw new Error('Ошибка загрузки расписания');
            return response.json();
        })
        .then(data => {
            loadingBlock.remove();

            if (!data.schedule || data.schedule.length === 0) {
                const noDataBlock = document.createElement('div');
                noDataBlock.className = 'schedule-date-block';
                noDataBlock.innerHTML = '<div class="date-header">Нет доступных занятий</div>';
                scheduleContainer.appendChild(noDataBlock);
                return;
            }

            const monthNames = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];

            const dates = {};
            data.schedule.forEach(item => {
                if (!dates[item.date]) dates[item.date] = [];
                dates[item.date].push(item);
            });

            const sortedDates = Object.keys(dates).sort();

            sortedDates.forEach(dateStr => {
                const date = new Date(dateStr);
                const times = dates[dateStr];
                const monthName = monthNames[date.getMonth()];
                const year = date.getFullYear();

                const dateBlock = document.createElement('div');
                dateBlock.className = 'schedule-date-block';

                const dateHeader = document.createElement('div');
                dateHeader.className = 'date-header';
                dateHeader.textContent = `${date.getDate()} ${monthName} ${year} года`;
                dateBlock.appendChild(dateHeader);

                const timeSlotsContainer = document.createElement('div');
                timeSlotsContainer.className = 'time-slots-container';

                times.forEach(slot => {
                    const timeSlot = document.createElement('div');
                    timeSlot.className = 'time-slot';

                    timeSlot.onclick = function() {
                        selectTime(slot, date);
                    };

                    const timeSpan = document.createElement('span');
                    timeSpan.className = 'time';
                    timeSpan.textContent = slot.time;

                    const seatsSpan = document.createElement('span');
                    seatsSpan.className = 'seats-info';
                    seatsSpan.textContent = `свободно ${slot.free_seats} из ${slot.max_seats}`;

                    timeSlot.appendChild(timeSpan);
                    timeSlot.appendChild(seatsSpan);
                    timeSlotsContainer.appendChild(timeSlot);
                });

                dateBlock.appendChild(timeSlotsContainer);
                scheduleContainer.appendChild(dateBlock);
            });

            setupTimeSlotStyles();
        })
        .catch(error => {
            console.error('Ошибка загрузки расписания:', error);
            loadingBlock.remove();
            const errorBlock = document.createElement('div');
            errorBlock.className = 'schedule-date-block';
            errorBlock.innerHTML = '<div class="date-header" style="color:red;">Ошибка загрузки</div>';
            scheduleContainer.appendChild(errorBlock);
        });
}

function selectTime(schedule, date) {
    selectedSchedule = schedule;

    const monthNames = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    const monthName = monthNames[date.getMonth()];

    alert(`✅ Вы выбрали: ${date.getDate()} ${monthName}, ${schedule.time}\n\nНажмите "Записаться" для подтверждения`);
}

function submitBooking() {
    if (!selectedSchedule) {
        alert('Пожалуйста, выберите время занятия');
        return;
    }

    let fullName, phone;
    if (isModal) {
        fullName = document.getElementById('modalFullName');
        phone = document.getElementById('modalPhone');
    } else {
        fullName = document.getElementById('fullName');
        phone = document.getElementById('phone');
    }

    if (!fullName || !phone) {
        alert('Элементы формы не найдены');
        return;
    }

    const fullNameValue = fullName.value.trim();
    const phoneValue = phone.value.trim();

    if (!fullNameValue) {
        alert('Введите ваше ФИО');
        fullName.focus();
        return;
    }

    if (!phoneValue || phoneValue.length < 10) {
        alert('Введите корректный номер телефона');
        phone.focus();
        return;
    }

    const bookingData = {
        schedule_id: selectedSchedule.id,
        full_name: fullNameValue,
        phone: phoneValue,
        child_name: '',
        child_age: 0,
        notes: ''
    };

    fetch('/api/booking/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(bookingData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Запись успешно создана!');
                if (isModal) {
                    closeModal();
                } else {
                    resetForm();
                }
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка при отправке');
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
    const fullName = document.getElementById('fullName');
    const phone = document.getElementById('phone');
    if (fullName) fullName.value = '';
    if (phone) phone.value = '';

    const groupSelect = document.getElementById('groupSelect');
    if (groupSelect) {
        groupSelect.value = '';
        resetSelectStyles(groupSelect);
    }

    const scheduleContainer = document.getElementById('scheduleContainer');
    if (scheduleContainer) {
        scheduleContainer.style.display = 'none';

        const existingDateBlocks = scheduleContainer.querySelectorAll('.schedule-date-block');
        existingDateBlocks.forEach(block => block.remove());

        const originalDateBlock = document.createElement('div');
        originalDateBlock.className = 'schedule-date-block';
        originalDateBlock.innerHTML = `
            <div class="date-header">07 февраля 2026 года</div>
            <div class="time-slots-container">
                <div class="time-slot">
                    <span class="time">10:00</span>
                    <span class="seats-info">свободно 4 из 5</span>
                </div>
                <div class="time-slot">
                    <span class="time">14:00</span>
                    <span class="seats-info">свободно 3 из 5</span>
                </div>
            </div>
        `;
        scheduleContainer.appendChild(originalDateBlock);
        setupTimeSlotStyles();
    }

    selectedSchedule = null;
}

document.addEventListener('DOMContentLoaded', function() {
    const originalRecord = document.querySelector('.record');
    if (originalRecord) {
        originalRecord.style.display = 'none';
    }

    const originalPrise = document.querySelector('.prise');
    if (originalPrise) {
        originalPrise.style.display = 'none';
    }

    const mainGroupSelect = document.getElementById('groupSelect');
    if (mainGroupSelect) {
        setupSelectStyles(mainGroupSelect);
    }

    setupTimeSlotStyles();

    const openButtons = document.querySelectorAll('.header_btn.open-modal-btn');
    openButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openModal();
        });
    });

    const priseButtons = document.querySelectorAll('.header_btn_prise');
    priseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openPriseModal();
        });
    });

    document.addEventListener('click', function(e) {
        if (e.target.id === 'modalOverlay' || e.target.id === 'modalClose') {
            closeModal();
        }
        if (e.target.id === 'priseModalOverlay' || e.target.id === 'priseModalClose') {
            closePriseModal();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modalContainer = document.getElementById('modalContainer');
            if (modalContainer && modalContainer.style.display === 'block') {
                closeModal();
            }
            const priseModalContainer = document.getElementById('priseModalContainer');
            if (priseModalContainer && priseModalContainer.style.display === 'block') {
                closePriseModal();
            }
        }
    });
});