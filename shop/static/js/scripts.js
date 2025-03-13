document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const slideCounter = document.querySelector('.slide-counter');

    let currentSlide = 0;
    let slideTimer;

    function showSlide(n) {
        // Сброс таймера при вызове функции
        clearTimeout(slideTimer);

        // Если перехожу с 3 или 1 слайда
        if (n >= slides.length) {
            currentSlide = 0;
        } else if (n < 0) {
            currentSlide = slides.length - 1;
        } else {
            currentSlide = n;
        }

        slides.forEach(slide => slide.style.display = 'none');
        slides[currentSlide].style.display = 'block';

        slideCounter.textContent = (currentSlide + 1) + '/' + slides.length;

        // Start timer for next automatic slide
        slideTimer = setTimeout(() => {
            showSlide(currentSlide + 1);
        }, 10000); // 10 seconds
    }

    function updateFromPrev() {
        showSlide(currentSlide - 1);
    }

    function updateFromNext() {
        showSlide(currentSlide + 1);
    }

    prevBtn.addEventListener('click', updateFromPrev);
    nextBtn.addEventListener('click', updateFromNext);

    // Initialize
    showSlide(currentSlide);
});