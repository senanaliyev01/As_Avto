// Hero Slider
const slides = document.querySelectorAll('.hero__slide');
const prevBtn = document.querySelector('.hero__arrow--prev');
const nextBtn = document.querySelector('.hero__arrow--next');
const dotsContainer = document.querySelector('.hero__dots');
let currentSlide = 0;

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
        if (dotsContainer.children[i]) {
            dotsContainer.children[i].classList.toggle('active', i === index);
        }
    });
}

function createDots() {
    slides.forEach((_, i) => {
        const dot = document.createElement('span');
        dot.classList.add('hero__dot');
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => {
            currentSlide = i;
            showSlide(currentSlide);
        });
        dotsContainer.appendChild(dot);
    });
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
}

nextBtn.addEventListener('click', nextSlide);
prevBtn.addEventListener('click', prevSlide);

createDots();
showSlide(currentSlide);

// Auto slide
autoSlide = setInterval(nextSlide, 6000);

// Pause on hover
const heroSlider = document.querySelector('.hero__slider');
heroSlider.addEventListener('mouseenter', () => clearInterval(autoSlide));
heroSlider.addEventListener('mouseleave', () => autoSlide = setInterval(nextSlide, 6000));

// Mobile Menu Toggle
const menuToggle = document.querySelector('.header__toggle');
const headerMenu = document.querySelector('.header__menu');
menuToggle.addEventListener('click', () => {
    headerMenu.classList.toggle('open');
    menuToggle.classList.toggle('open');
});

// Smooth Scroll for anchor links
const anchorLinks = document.querySelectorAll('a[href^="#"]');
anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
}); 