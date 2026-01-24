function createModalFromExisting() {
    const originalRecord = document.querySelector('.record');
    if (!originalRecord) {
        console.log('Элемент .record не найден на странице');
        return null;
    }

    originalRecord.style.display = 'none';

    const clonedRecord = originalRecord.cloneNode(true);
    clonedRecord.classList.add('modal-record');
    clonedRecord.style.display = 'block';

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
    if (!originalPrise) {
        console.log('Элемент .prise не найден на странице');
        return null;
    }

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
    console.log('openModal вызвана');
    let modalContainer = document.getElementById('modalContainer');

    if (!modalContainer) {
        console.log('Создаем модальное окно записи');
        modalContainer = createModalFromExisting();
        if (!modalContainer) return;
    }

    const priseModalContainer = document.getElementById('priseModalContainer');
    if (priseModalContainer) {
        priseModalContainer.style.display = 'none';
    }

    modalContainer.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function openPriseModal() {
    console.log('openPriseModal вызвана');
    let modalContainer = document.getElementById('priseModalContainer');

    if (!modalContainer) {
        console.log('Создаем модальное окно прайса');
        modalContainer = createPriseModal();
        if (!modalContainer) return;
    }

    const recordModalContainer = document.getElementById('modalContainer');
    if (recordModalContainer) {
        recordModalContainer.style.display = 'none';
    }

    modalContainer.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modalContainer = document.getElementById('modalContainer');
    if (!modalContainer) return;

    modalContainer.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function closePriseModal() {
    const modalContainer = document.getElementById('priseModalContainer');
    if (!modalContainer) return;

    modalContainer.style.display = 'none';
    document.body.style.overflow = 'auto';
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен');

    const originalRecord = document.querySelector('.record');
    if (originalRecord) {
        originalRecord.style.display = 'none';
    }

    const originalPrise = document.querySelector('.prise');
    if (originalPrise) {
        originalPrise.style.display = 'none';
    }

    const openButtons = document.querySelectorAll('.header_btn.open-modal-btn');
    console.log('Найдено кнопок записи:', openButtons.length);

    openButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Клик по кнопке записи');
            e.preventDefault();
            openModal();
        });
    });

    const priseButtons = document.querySelectorAll('.header_btn_prise');
    console.log('Найдено кнопок прайса:', priseButtons.length);

    priseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Клик по кнопке прайса');
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