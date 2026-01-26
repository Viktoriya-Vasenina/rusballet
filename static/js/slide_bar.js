document.addEventListener('DOMContentLoaded', function() {
    const teacherPhoto = document.getElementById('teacher-photo');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (!teacherPhoto || !prevBtn || !nextBtn) {
        return;
    }

    const currentSrc = teacherPhoto.src;
    const basePath = currentSrc.substring(0, currentSrc.lastIndexOf('/') + 1);

    const teachersData = [{
            name: "Полина Некрасова",
            education: "Выпускница МГАХ как артист балета (педагог Сырова И.Ю.), а также как педагог-хореограф. Артистка Большого Театра России",
            experienceCount: "15",
            experienceText: "лет опыта преподавания",
            awardsCount: "05",
            awardsText: "профессиональных наград",
            achievementsCount: "18",
            achievementsText: "учеников призеров",
            photo: "teacher_slide.png"
        },
        {
            name: "Анна Смирнова",
            education: "Выпускница Московской государственной академии хореографии, лауреат международных конкурсов, педагог-репетитор Мариинского театра",
            experienceCount: "12",
            experienceText: "лет опыта преподавания",
            awardsCount: "08",
            awardsText: "профессиональных наград",
            achievementsCount: "24",
            achievementsText: "ученика призеров международных конкурсов",
            photo: "teacher_slide_2.png"
        },
        {
            name: "Ирина Волкова",
            education: "Заслуженная артистка России, выпускница Академии русского балета им. Вагановой, педагог с международным опытом работы",
            experienceCount: "20",
            experienceText: "лет опыта преподавания",
            awardsCount: "12",
            awardsText: "профессиональных наград",
            achievementsCount: "32",
            achievementsText: "ученика в труппах ведущих театров",
            photo: "teacher_slide_3.png"
        }
    ];

    const teacherName = document.getElementById('teacher-name');
    const teacherEducation = document.getElementById('teacher-education');
    const teacherExperienceCount = document.getElementById('teacher-experience-count');
    const teacherExperienceText = document.getElementById('teacher-experience-text');
    const teacherAwardsCount = document.getElementById('teacher-awards-count');
    const teacherAwardsText = document.getElementById('teacher-awards-text');
    const teacherAchievementsCount = document.getElementById('teacher-achievements-count');
    const teacherAchievementsText = document.getElementById('teacher-achievements-text');

    let currentSlideIndex = 0;

    function updateSlideContent() {
        const teacher = teachersData[currentSlideIndex];

        if (teacherName) teacherName.textContent = teacher.name;
        if (teacherEducation) teacherEducation.textContent = teacher.education;
        if (teacherExperienceCount) teacherExperienceCount.textContent = teacher.experienceCount;
        if (teacherExperienceText) teacherExperienceText.textContent = teacher.experienceText;
        if (teacherAwardsCount) teacherAwardsCount.textContent = teacher.awardsCount;
        if (teacherAwardsText) teacherAwardsText.textContent = teacher.awardsText;
        if (teacherAchievementsCount) teacherAchievementsCount.textContent = teacher.achievementsCount;
        if (teacherAchievementsText) teacherAchievementsText.textContent = teacher.achievementsText;

        const newImagePath = basePath + teacher.photo;
        teacherPhoto.src = newImagePath;
        teacherPhoto.alt = teacher.name;
    }

    function showPrevSlide() {
        currentSlideIndex--;
        if (currentSlideIndex < 0) {
            currentSlideIndex = teachersData.length - 1;
        }
        updateSlideContent();
    }

    function showNextSlide() {
        currentSlideIndex++;
        if (currentSlideIndex >= teachersData.length) {
            currentSlideIndex = 0;
        }
        updateSlideContent();
    }

    prevBtn.addEventListener('click', showPrevSlide);
    nextBtn.addEventListener('click', showNextSlide);

    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') showPrevSlide();
        if (e.key === 'ArrowRight') showNextSlide();
    });

    updateSlideContent();
});