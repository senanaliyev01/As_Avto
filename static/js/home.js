//home 

document.addEventListener('DOMContentLoaded', function() {
    // Hero Slider functionality
    const slides = document.querySelectorAll('.hero__slide');
    const prevBtn = document.querySelector('.hero__arrow--prev');
    const nextBtn = document.querySelector('.hero__arrow--next');
    const dotsContainer = document.querySelector('.hero__dots');
    
    let currentIndex = 0;
    let interval;
    const intervalTime = 5000; // Change slide every 5 seconds
    
    // Create dots based on number of slides
    function createDots() {
        slides.forEach((_, index) => {
            const dot = document.createElement('span');
            dot.classList.add('hero__dot');
            if (index === 0) {
                dot.classList.add('active');
            }
            dot.addEventListener('click', () => {
                goToSlide(index);
                resetInterval();
            });
            dotsContainer.appendChild(dot);
        });
    }
    
    // Set active slide
    function goToSlide(index) {
        // Remove active class from all slides and dots
        slides.forEach(slide => slide.classList.remove('active'));
        document.querySelectorAll('.hero__dot').forEach(dot => dot.classList.remove('active'));
        
        // Add active class to current slide and dot
        slides[index].classList.add('active');
        document.querySelectorAll('.hero__dot')[index].classList.add('active');
        
        currentIndex = index;
    }
    
    // Next slide
    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        goToSlide(currentIndex);
    }
    
    // Previous slide
    function prevSlide() {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        goToSlide(currentIndex);
    }
    
    // Reset interval
    function resetInterval() {
        clearInterval(interval);
        interval = setInterval(nextSlide, intervalTime);
    }
    
    // Event listeners
    prevBtn.addEventListener('click', () => {
        prevSlide();
        resetInterval();
    });
    
    nextBtn.addEventListener('click', () => {
        nextSlide();
        resetInterval();
    });
    
    // Initialize slider
    createDots();
    resetInterval();
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.header__toggle');
    const headerNav = document.querySelector('.header__nav');
    
    menuToggle.addEventListener('click', function() {
        headerNav.classList.toggle('active');
        menuToggle.classList.toggle('active');
    });
}); 
