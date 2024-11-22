let currentSlideIndex = 0;
const slides = document.querySelectorAll('.carousel-slide');

function showSlide(index) {
    const carousel = document.querySelector('.carousel');
    if (index >= slides.length) {
        currentSlideIndex = 0;
    } else if (index < 0) {
        currentSlideIndex = slides.length - 1;
    } else {
        currentSlideIndex = index;
    }
    const offset = -currentSlideIndex * 100;
    carousel.style.transform = `translateX(${offset}%)`;
}

function moveSlide(step) {
    showSlide(currentSlideIndex + step);
}


showSlide(currentSlideIndex);
