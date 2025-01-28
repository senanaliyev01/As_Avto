// Swiper konfiqurasiyası
const swiperConfig = {
    slidesPerView: 'auto',
    spaceBetween: 30,
    centeredSlides: true,
    loop: true,
    autoplay: {
        delay: 3000,
        disableOnInteraction: false
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true
    },
    breakpoints: {
        320: {
            slidesPerView: 1,
            spaceBetween: 10
        },
        480: {
            slidesPerView: 2,
            spaceBetween: 20
        },
        768: {
            slidesPerView: 3,
            spaceBetween: 30
        },
        1024: {
            slidesPerView: 4,
            spaceBetween: 40
        }
    }
};

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', function() {
    // Swiper-ləri inicializasiya et
    if (document.querySelector('.brandsSwiper')) {
        new Swiper('.brandsSwiper', swiperConfig);
    }
    if (document.querySelector('.carBrandsSwiper')) {
        new Swiper('.carBrandsSwiper', {
            ...swiperConfig,
            autoplay: {
                ...swiperConfig.autoplay,
                delay: 3500
            }
        });
    }
});


