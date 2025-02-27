document.addEventListener('DOMContentLoaded', function() {
    // Hero Slider
    const heroSwiper = new Swiper('.hero-slider', {
        slidesPerView: 1,
        loop: true,
        effect: 'fade',
        speed: 1000,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        fadeEffect: {
            crossFade: true
        },
        on: {
            init: function () {
                let activeSlide = this.slides[this.activeIndex];
                activeSlide.classList.add('swiper-slide-animated');
            },
            slideChangeTransitionStart: function () {
                let activeSlide = this.slides[this.activeIndex];
                activeSlide.classList.add('swiper-slide-animated');
            },
            slideChangeTransitionEnd: function () {
                let prevSlide = this.slides[this.previousIndex];
                if (prevSlide) {
                    prevSlide.classList.remove('swiper-slide-animated');
                }
            }
        }
    });

    // Initialize Swiper
    const swiper = new Swiper('.new-products-slider', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        breakpoints: {
            640: {
                slidesPerView: 2,
            },
            768: {
                slidesPerView: 3,
            },
            1024: {
                slidesPerView: 4,
            },
        },
    });
});