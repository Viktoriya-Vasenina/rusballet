function compensateScrollbar() {
    if (document.body.dataset.scrollbarCompensated) return;

    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.paddingRight = `${scrollbarWidth}px`;

    const headerImg = document.querySelector('.header img');
    if (headerImg) {
        const computedStyle = window.getComputedStyle(headerImg);
        document.body.dataset.headerImgOriginalMarginRight = computedStyle.marginRight;
        const currentMarginValue = parseInt(computedStyle.marginRight) || -70;
        headerImg.style.marginRight = `${currentMarginValue - scrollbarWidth}px`;
    }

    const header = document.querySelector('.header');
    if (header) {
        const computedStyle = window.getComputedStyle(header);
        document.body.dataset.headerOriginalPaddingRight = computedStyle.paddingRight;
        header.style.paddingRight = `${scrollbarWidth}px`;
    }

    document.body.dataset.scrollbarCompensated = 'true';
}

function restoreScrollbar() {
    document.body.style.paddingRight = '';
    document.body.style.overflow = 'auto';

    const headerImg = document.querySelector('.header img');
    if (headerImg && document.body.dataset.headerImgOriginalMarginRight !== undefined) {
        headerImg.style.marginRight = document.body.dataset.headerImgOriginalMarginRight;
        delete document.body.dataset.headerImgOriginalMarginRight;
    }

    const header = document.querySelector('.header');
    if (header && document.body.dataset.headerOriginalPaddingRight !== undefined) {
        header.style.paddingRight = document.body.dataset.headerOriginalPaddingRight;
        delete document.body.dataset.headerOriginalPaddingRight;
    }

    delete document.body.dataset.scrollbarCompensated;
}

function openModal() {
    let modalContainer = document.getElementById('modalContainer');
    if (!modalContainer) {
        modalContainer = createModalFromExisting();
        if (!modalContainer) return;
    }

    compensateScrollbar();

    const priseModalContainer = document.getElementById('priseModalContainer');
    if (priseModalContainer) priseModalContainer.style.display = 'none';

    modalContainer.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function openPriseModal() {
    let modalContainer = document.getElementById('priseModalContainer');
    if (!modalContainer) {
        modalContainer = createPriseModal();
        if (!modalContainer) return;
    }

    compensateScrollbar();

    const recordModalContainer = document.getElementById('modalContainer');
    if (recordModalContainer) recordModalContainer.style.display = 'none';

    modalContainer.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modalContainer = document.getElementById('modalContainer');
    if (!modalContainer) return;

    modalContainer.style.display = 'none';

    const priseModalContainer = document.getElementById('priseModalContainer');
    if (!priseModalContainer || priseModalContainer.style.display === 'none') {
        restoreScrollbar();
    }
}

function closePriseModal() {
    const modalContainer = document.getElementById('priseModalContainer');
    if (!modalContainer) return;

    modalContainer.style.display = 'none';

    const recordModalContainer = document.getElementById('modalContainer');
    if (!recordModalContainer || recordModalContainer.style.display === 'none') {
        restoreScrollbar();
    }
}