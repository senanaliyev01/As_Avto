      // CSRF token funksiyası
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

    // İstifadəçi sayı animasiyası
    function animateCount(element, target) {
        const start = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 saniyə
        const steps = 20;
        const increment = (target - start) / steps;
        let current = start;
        let step = 0;

        const animate = () => {
            step++;
            current += increment;
            element.textContent = Math.round(current);

            if (step < steps) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = target;
            }
        };

        animate();
    }

    // Statistika yeniləmə funksiyası
    function updateStatistics() {
        fetch('/get_statistics/', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Hər bir1 statistika kartını yenilə
            Object.keys(data).forEach(key => {
                const element = document.querySelector(`.statistics-card .count[data-type="${key}"]`);
                if (element) {
                    const currentValue = parseInt(element.textContent) || 0;
                    const newValue = data[key];
                    
                    if (currentValue !== newValue) {
                        // Kartı vurğula
                        const card = element.closest('.statistics-card');
                        card.classList.add('updating');
                        
                        // Sayı animasiyası
                        animateCount(element, newValue);
                        
                        // Animasiyanı təmizlə
                        setTimeout(() => {
                            card.classList.remove('updating');
                        }, 8000);
                    }
                }
            });
        })
        .catch(error => {
            console.error('Statistika yeniləmə xətası:', error);
            setTimeout(updateStatistics, 3600000); // 1 saatdan sonra yenidən cəhd et
        });
    }

    // Rəy bildirişi funksiyası
    function showReviewNotification(type, message) {
        const existingNotification = document.querySelector('.review-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `review-notification ${type}`;
        notification.innerHTML = `
            <div class="icon">
                <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-circle'}"></i>
            </div>
            <div class="content">
                <h4>${type === 'success' ? 'Uğurlu!' : 'Xəta!'}</h4>
                <p>${message}</p>
            </div>
            <div class="progress">
                <div class="progress-bar"></div>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 3000);
    }

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

    // Saat elementlərini əldə et
    const currentTimeElement = document.getElementById('current-time');

    // Təkmilləşdirilmiş saat funksiyası
    function updateCurrentTime() {
        if (currentTimeElement) {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            
            // Animasiyalı rəqəm dəyişməsi
            currentTimeElement.innerHTML = `
                <span class="time-unit">${hours}</span>:
                <span class="time-unit">${minutes}</span>:
                <span class="time-unit">${seconds}</span>
            `;
        }
    }

    // İş saatlarını yoxla və bildiriş göstər
    function checkWorkingHours() {
        const now = new Date();
        const currentHour = now.getHours();
        const isWorkingHours = currentHour >= 9 && currentHour < 18;
        
        const workingHoursElement = document.querySelector('.working-hours p:first-child');
        if (workingHoursElement) {
            workingHoursElement.style.color = isWorkingHours ? '#4caf50' : '#ff5252';
            workingHoursElement.innerHTML = `İş vaxtımız: 09:00 - 18:00 
                <span class="status-badge" style="margin-left: 10px; font-size: 0.9em;">
                    ${isWorkingHours ? '🟢 Açıqdır' : '🔴 Bağlıdır'}
                </span>`;
        }
    }

    // Səbət sayını yenilə
    function updateCartCount() {
        fetch('/get_cart_count/')
            .then(response => response.json())
            .then(data => {
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Mesaj animasiyası
    function showAnimatedMessage(message, isError = false, mehsulData = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'animated-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${!isError ? `
                    <div class="success-checkmark">
                        <div class="check-icon">
                            <i class="fas fa-check"></i>
                        </div>
                    </div>
                    <div class="message-text">
                        ${message}
                        ${mehsulData && mehsulData.adi ? `
                            <div class="product-info">
                                ${mehsulData.sekil ? 
                                    `<img src="${mehsulData.sekil}" alt="${mehsulData.adi}" class="product-image">` 
                                    : ''
                                }
                                <span class="product-name">${mehsulData.adi}</span>
                                <span class="product-name">${mehsulData.oem}</span>
                            </div>
                        ` : ''}
                    </div>
                ` : `
                    <div class="error-icon">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div class="message-text">${message}</div>
                `}
            </div>
        `;

        // Stil əlavə et
        Object.assign(messageDiv.style, {
            position: 'fixed',
            top: '20px',
            right: '-400px',
            backgroundColor: isError ? '#dc3545' : '#003366',
            color: '#ffffff',
            padding: '15px 25px',
            borderRadius: '8px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.15)',
            zIndex: '2000',
            transition: 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            minWidth: '300px',
            border: isError ? 'none' : '1px solid #eee'
        });

        // CSS stilləri əlavə et
        const style = document.createElement('style');
        style.textContent = `
            .animated-message {
                display: flex;
                align-items: center;
            }
            .message-content {
                display: flex;
                align-items: center;
                gap: 15px;
                width: 100%;
            }
            .message-text {
                font-size: 1rem;
                font-weight: 500;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .success-checkmark {
                width: 30px;
                height: 30px;
                position: relative;
            }
            .check-icon {
                width: 30px;
                height: 30px;
                position: relative;
                border-radius: 50%;
                background-color: #4CAF50;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: pop 0.5s forwards;
            }
            .check-icon i {
                color: white;
                font-size: 16px;
            }
            @keyframes pop {
                0% { transform: scale(0) }
                50% { transform: scale(1.2) }
                100% { transform: scale(1) }
            }
            .product-info {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 10px 0;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 6px;
            }
            
            .product-image {
                width: 80px;
                height: auto;
                object-fit: cover;
            }
            
            .product-name {
                font-size: 0.9em;
                font-weight: 500;
                color: #495057;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(messageDiv);

        // Mesajın görünməsi
        requestAnimationFrame(() => {
            messageDiv.style.right = '20px';
            messageDiv.style.transform = 'translateY(0)';
        });

        // 3 saniyədən sonra mesajın yox olması
        setTimeout(() => {
            messageDiv.style.right = '-400px';
            messageDiv.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 500);
        }, 3000);
    }

    // DOM yükləndikdə
    document.addEventListener('DOMContentLoaded', () => {
        try {
            // Saatı başlat
            updateCurrentTime();
            setInterval(updateCurrentTime, 1000);

            // İş saatlarını yoxla
            checkWorkingHours();
            setInterval(checkWorkingHours, 60000); // Hər dəqiqə yoxla

            // Səbət sayını yenilə
            updateCartCount();

            // Səbətə məhsul əlavə etmək
            const cartLinks = document.querySelectorAll('.cart-icon');

            cartLinks.forEach(link => {
                link.addEventListener('click', function (event) {
                    event.preventDefault();

                    const originalContent = this.innerHTML;
                    const url = this.getAttribute('href');

                    // Loading effektini göstər
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    this.style.pointerEvents = 'none';
                    this.style.opacity = '0.7';

                    // 2 saniyə loading göstər
                    setTimeout(() => {
                        fetch(url)
                            .then(response => response.json())
                            .then(data => {
                                // Original ikonu bərpa et
                                this.innerHTML = originalContent;
                                this.style.pointerEvents = 'auto';
                                this.style.opacity = '1';

                                if (data.success) {
                                    showAnimatedMessage(
                                        "Məhsul səbətə əlavə olundu!", 
                                        false, 
                                        data.mehsul
                                    );
                                    updateCartCount();
                                } else {
                                    showAnimatedMessage(
                                        data.error || "Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.", 
                                        true
                                    );
                                }
                            })
                            .catch(error => {
                                console.error("Xəta:", error);
                                this.innerHTML = originalContent;
                                this.style.pointerEvents = 'auto';
                                this.style.opacity = '1';
                                showAnimatedMessage("Serverdə xəta baş verdi.", true);
                            });
                    }, 2000);
                });
            });

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

            // İlkin statistikaları yüklə
            updateStatistics();
            setInterval(updateStatistics, 3600000); // 1 saatdan bir yenilə

            // Rəy formu
            const reviewForm = document.querySelector('.review-form form');
            if (reviewForm) {
                reviewForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const rating = reviewForm.querySelector('input[name="qiymetlendirme"]:checked');
                    if (!rating) {
                        showAnimatedMessage('Zəhmət olmasa, qiymətləndirmə üçün ulduz seçin', true);
                        return;
                    }

                    const review = reviewForm.querySelector('textarea[name="rey"]').value.trim();
                    if (!review) {
                        showAnimatedMessage('Zəhmət olmasa, rəyinizi yazın', true);
                        return;
                    }

                    const formData = new FormData(reviewForm);
                    
                    fetch(reviewForm.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showAnimatedMessage('Rəyiniz uğurla göndərildi. Təsdiqlənməsi gözlənilir', false);
                            reviewForm.reset();
                            setTimeout(() => {
                                window.location.reload();
                            }, 3000);
                        } else {
                            showAnimatedMessage(data.message || 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin', true);
                        }
                    })
                    .catch(error => {
                        console.error('Xəta:', error);
                        showAnimatedMessage('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin', true);
                    });
                });
            }

        } catch (error) {
            console.error('Funksiya xətası:', error);
        }
    });


   
    
    document.getElementById('search-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Formun dərhal göndərilməsini dayandır
    
        let searchButton = document.getElementById('search-button');
        let spinner = document.getElementById('loading-spinner');
    
        // Butonun ölçüsünü qorumaq üçün enini və hündürlüyünü sabit saxla
        searchButton.style.width = `${searchButton.offsetWidth}px`;
        searchButton.style.height = `${searchButton.offsetHeight}px`;
        
        // Axtarış yazısını gizlət, amma spinneri saxla
        searchButton.childNodes[0].nodeValue = ''; // Axtar sözünü sil
        spinner.style.display = 'inline-block'; // Spinneri göstər
    
        // Butonu deaktiv et ki, yenidən klik olunmasın
        searchButton.disabled = true; 
    
        // 2 saniyə sonra formu göndər
        setTimeout(() => {
            this.submit(); // Formu göndər
        }, 2000);
    });
    

    function confirmLogout(event) {
        event.preventDefault();  // Default davranışı dayandırır
        if (confirm("Çıxış etmək istədiyinizə əminsiniz?")) {
            fetch(event.target.href, {  // URL burada event.target.href-dən alınır
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            }).then(response => {
                if (response.ok) {
                    window.location.href = '/';  // Çıxış etdikdən sonra ana səhifəyə yönləndirin
                } else {
                    alert('Çıxış zamanı xəta baş verdi. Yenidən cəhd edin.');
                }
            }).catch(error => {
                console.error('Xəta:', error);
                alert('Çıxış zamanı xəta baş verdi. Yenidən cəhd edin.');
            });
        }
    }


