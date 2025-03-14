document.addEventListener('DOMContentLoaded', function() {
    // Hero Slider
    try {
        if (document.querySelector('.hero-slider')) {
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
                pagination: {
                    el: '.hero-pagination',
                    clickable: true,
                    renderBullet: function (index, className) {
                        return '<span class="' + className + '"></span>';
                    },
                },
                navigation: {
                    nextEl: '.hero-button-next',
                    prevEl: '.hero-button-prev',
                },
                on: {
                    init: function () {
                        let activeSlide = this.slides[this.activeIndex];
                        if (activeSlide) {
                            activeSlide.classList.add('swiper-slide-animated');
                        }
                    },
                    slideChangeTransitionStart: function () {
                        let activeSlide = this.slides[this.activeIndex];
                        if (activeSlide) {
                            activeSlide.classList.add('swiper-slide-animated');
                        }
                    },
                    slideChangeTransitionEnd: function () {
                        if (typeof this.previousIndex !== 'undefined') {
                            let prevSlide = this.slides[this.previousIndex];
                            if (prevSlide) {
                                prevSlide.classList.remove('swiper-slide-animated');
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Hero Slider xətası:', error);
    }

    // Initialize Swiper
    try {
        if (document.querySelector('.new-products-slider')) {
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
        }
    } catch (error) {
        console.error('New Products Slider xətası:', error);
    }
});













