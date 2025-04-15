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

    // Yeni Məhsullar Slider
    try {
        if (document.querySelector('.new-products-slider')) {
            const newProductsSwiper = new Swiper('.new-products-slider', {
                slidesPerView: 1,
                spaceBetween: 30,
                loop: true,
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                    renderBullet: function (index, className) {
                        return '<span class="' + className + '"></span>';
                    },
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
                        spaceBetween: 20,
                    },
                    768: {
                        slidesPerView: 3,
                        spaceBetween: 30,
                    },
                    1024: {
                        slidesPerView: 4,
                        spaceBetween: 40,
                    },
                },
                on: {
                    init: function () {
                        this.slides.forEach(slide => {
                            slide.style.opacity = '0';
                            slide.style.transform = 'translateY(20px)';
                        });
                        this.slides[this.activeIndex].style.opacity = '1';
                        this.slides[this.activeIndex].style.transform = 'translateY(0)';
                    },
                    slideChangeTransitionStart: function () {
                        this.slides.forEach(slide => {
                            slide.style.opacity = '0';
                            slide.style.transform = 'translateY(20px)';
                        });
                    },
                    slideChangeTransitionEnd: function () {
                        this.slides[this.activeIndex].style.opacity = '1';
                        this.slides[this.activeIndex].style.transform = 'translateY(0)';
                    }
                }
            });
        }
    } catch (error) {
        console.error('Yeni Məhsullar Slider xətası:', error);
    }

    // Miqdar validasiyası
    function validateQuantity(input) {
        const value = parseInt(input.value);
        const min = parseInt(input.min);
        const max = parseInt(input.max);
        const errorDiv = input.nextElementSibling;
        
        if (isNaN(value) || value < min) {
            input.value = min;
            errorDiv.textContent = 'Minimum miqdar: ' + min;
            errorDiv.style.display = 'block';
            return false;
        }
        
        if (value > max) {
            input.value = max;
            errorDiv.textContent = 'Maksimum miqdar: ' + max;
            errorDiv.style.display = 'block';
            return false;
        }
        
        errorDiv.style.display = 'none';
        return true;
    }

    // Səbətə əlavə etmə
    function addToCartWithQuantity(productId) {
        const quantityInput = document.querySelector(`.new-quantity-input[data-product-id="${productId}"]`);
        const quantity = parseInt(quantityInput.value);
        
        if (!validateQuantity(quantityInput)) {
            return;
        }

        // Səbətə əlavə etmə animasiyası
        const button = quantityInput.closest('.new-product-actions').querySelector('.new-cart-button');
        button.classList.add('adding-to-cart');
        
        // Burada səbətə əlavə etmə API çağırışı olacaq
        fetch('/sebet/elave-et/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Uğurlu əlavə etmə animasiyası
                button.classList.remove('adding-to-cart');
                button.classList.add('added-to-cart');
                setTimeout(() => {
                    button.classList.remove('added-to-cart');
                }, 2000);
                
                // Səbət sayını yenilə
                updateCartCount(data.cart_count);
            } else {
                throw new Error(data.error || 'Xəta baş verdi');
            }
        })
        .catch(error => {
            console.error('Səbətə əlavə etmə xətası:', error);
            button.classList.remove('adding-to-cart');
            const errorDiv = quantityInput.nextElementSibling;
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        });
    }

    // CSRF token almaq üçün köməkçi funksiya
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Səbət sayını yeniləmə
    function updateCartCount(count) {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = count;
            cartCountElement.style.display = count > 0 ? 'block' : 'none';
        }
    }
});













