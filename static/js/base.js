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
            // Hər bir statistika kartını yenilə
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
                        }, 1000);
                    }
                }
            });
        })
        .catch(error => {
            console.error('Statistika yeniləmə xətası:', error);
            setTimeout(updateStatistics, 1000);
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
            backgroundColor: isError ? '#dc3545' : '#ffffff',
            color: isError ? '#ffffff' : '#333333',
            padding: '15px 25px',
            borderRadius: '8px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.15)',
            zIndex: '1000',
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
            .checkout-icon {
                display: flex;
                align-items: center;
                gap: 5px;
                margin-top: 5px;
                color: #4CAF50;
                font-size: 0.9em;
            }
            .checkout-icon i {
                animation: cartBounce 1s ease-in-out;
            }
            .checkout-plus {
                color: #4CAF50;
                font-weight: bold;
                animation: plusPulse 1s ease-in-out;
            }
            .checkout-item {
                width: 8px;
                height: 8px;
                background-color: #4CAF50;
                border-radius: 50%;
                animation: itemSlide 1s ease-in-out;
            }
            @keyframes cartBounce {
                0%, 20%, 50%, 80%, 100% {
                    transform: translateY(0);
                }
                40% {
                    transform: translateY(-5px);
                }
                60% {
                    transform: translateY(-3px);
                }
            }
            @keyframes plusPulse {
                0%, 100% {
                    transform: scale(1);
                    opacity: 1;
                }
                50% {
                    transform: scale(1.5);
                    opacity: 0.7;
                }
            }
            @keyframes itemSlide {
                0% {
                    transform: translateX(-20px);
                    opacity: 0;
                }
                50% {
                    opacity: 1;
                }
                100% {
                    transform: translateX(0);
                    opacity: 1;
                }
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
                width: 50px;
                height: 50px;
                object-fit: cover;
                border-radius: 4px;
                border: 1px solid #dee2e6;
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

    // Axtarış nəticələrini göstərmək üçün funksiya
    function showSearchResults(results, searchQuery) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'animated-message search-results-modal';
        
        let productsHtml = '';
        if (results.length > 0) {
            productsHtml = results.map(product => `
                <div class="search-product-item">
                    <div class="product-image">
                        ${product.sekil ? 
                            `<img src="${product.sekil}" alt="${product.adi}">` : 
                            '<i class="fas fa-image"></i>'
                        }
                    </div>
                    <div class="product-details">
                        <h4>${product.adi}</h4>
                        <p class="product-oem">${product.oem || 'OEM: Məlumat yoxdur'}</p>
                        <p class="product-price">${product.qiymet ? product.qiymet + ' AZN' : 'Qiymət: Sorğu ilə'}</p>
                    </div>
                </div>
            `).join('');
        } else {
            productsHtml = '<p class="no-results">Heç bir nəticə tapılmadı</p>';
        }

        messageDiv.innerHTML = `
            <div class="search-results-content">
                <div class="search-header">
                    <div class="search-info">
                        <h3>Axtarış Nəticələri</h3>
                        <p class="search-query">"${searchQuery}" üçün ${results.length} nəticə tapıldı</p>
                    </div>
                    <button class="close-button">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="search-results-list">
                    ${productsHtml}
                </div>
            </div>
        `;

        // Stil əlavə et
        Object.assign(messageDiv.style, {
            position: 'fixed',
            top: '50%',
            right: '-100%',
            transform: 'translateY(-50%)',
            backgroundColor: '#ffffff',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
            zIndex: '1000',
            transition: 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            maxWidth: '90%',
            width: '500px',
            maxHeight: '80vh',
            overflowY: 'auto'
        });

        // CSS stilləri əlavə et
        const style = document.createElement('style');
        style.textContent = `
            .search-results-modal {
                background: rgba(255, 255, 255, 0.98);
            }
            .search-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #eee;
            }
            .search-info h3 {
                margin: 0;
                color: #0a192f;
                font-size: 1.5rem;
                font-weight: 600;
            }
            .search-query {
                margin: 5px 0 0;
                color: #666;
                font-size: 0.9rem;
            }
            .close-button {
                background: none;
                border: none;
                color: #666;
                font-size: 1.2rem;
                cursor: pointer;
                padding: 5px;
                transition: color 0.3s ease;
            }
            .close-button:hover {
                color: #dc3545;
            }
            .search-results-list {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .search-product-item {
                display: flex;
                gap: 15px;
                padding: 15px;
                border-radius: 8px;
                background: #f8f9fa;
                transition: transform 0.3s ease;
                animation: slideIn 0.5s forwards;
                opacity: 0;
            }
            .search-product-item:hover {
                transform: translateX(5px);
                background: #f0f0f0;
            }
            .product-image {
                width: 80px;
                height: 80px;
                border-radius: 8px;
                overflow: hidden;
                background: #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #ddd;
            }
            .product-image img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .product-image i {
                font-size: 2rem;
                color: #ddd;
            }
            .product-details {
                flex: 1;
            }
            .product-details h4 {
                margin: 0 0 5px;
                color: #0a192f;
                font-size: 1.1rem;
            }
            .product-oem {
                margin: 0 0 5px;
                color: #666;
                font-size: 0.9rem;
            }
            .product-price {
                margin: 0;
                color: #28a745;
                font-weight: 600;
                font-size: 1rem;
            }
            .no-results {
                text-align: center;
                color: #666;
                padding: 20px;
                font-size: 1.1rem;
            }
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(messageDiv);

        // Animasiya ilə göstər
        setTimeout(() => {
            messageDiv.style.right = '20px';
        }, 100);

        // Hər bir məhsul elementini ardıcıl animate et
        const products = messageDiv.querySelectorAll('.search-product-item');
        products.forEach((product, index) => {
            setTimeout(() => {
                product.style.opacity = '1';
            }, 100 * (index + 1));
        });

        // Bağlama düyməsini aktivləşdir
        const closeButton = messageDiv.querySelector('.close-button');
        closeButton.addEventListener('click', () => {
            messageDiv.style.right = '-100%';
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 500);
        });

        // Klik hadisəsini əlavə et
        document.addEventListener('click', function(event) {
            if (!messageDiv.contains(event.target) && event.target !== messageDiv) {
                messageDiv.style.right = '-100%';
                setTimeout(() => {
                    if (messageDiv.parentNode) {
                        document.body.removeChild(messageDiv);
                    }
                }, 500);
            }
        });
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
            setInterval(updateStatistics, 1000);

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

            // Axtarış forması
            const searchForm = document.querySelector('.search-form');
            if (searchForm) {
                const searchButton = searchForm.querySelector('#search-button');
                const originalButtonText = searchButton.innerHTML;

                searchForm.addEventListener('submit', function(e) {
                    e.preventDefault();

                    // Loading effektini göstər
                    searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Axtarılır...';
                    searchButton.disabled = true;

                    const formData = new FormData(this);
                    const searchQuery = formData.get('search_query');

                    // 2 saniyə gözlə
                    setTimeout(() => {
                        fetch(this.action + '?' + new URLSearchParams(formData).toString())
                            .then(response => response.json())
                            .then(data => {
                                // Buttonu normal vəziyyətə qaytar
                                searchButton.innerHTML = originalButtonText;
                                searchButton.disabled = false;

                                // Nəticələri göstər
                                showSearchResults(data.results || [], searchQuery);
                            })
                            .catch(error => {
                                console.error('Xəta:', error);
                                searchButton.innerHTML = originalButtonText;
                                searchButton.disabled = false;
                                showAnimatedMessage('Axtarış zamanı xəta baş verdi', true);
                            });
                    }, 2000);
                });
            }

        } catch (error) {
            console.error('Funksiya xətası:', error);
        }
    });