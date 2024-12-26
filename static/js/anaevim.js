let currentIndex = 0;
const slides = document.querySelectorAll('.slider .slide');
const totalSlides = slides.length;

function showSlide(index) {
    const slider = document.querySelector('.slider');
    slider.style.transform = `translateX(-${index * 100}%)`;
}

document.querySelector('.next').addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % totalSlides;
    showSlide(currentIndex);
});

document.querySelector('.prev').addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
    showSlide(currentIndex);
});

setInterval(() => {
    currentIndex = (currentIndex + 1) % totalSlides;
    showSlide(currentIndex);
}, 3000);

function showNotification(message, type) {
    const notification = document.querySelector('.notification');
    notification.textContent = message;
    notification.classList.add('show', type);
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}