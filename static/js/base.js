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
                                    `<img src="${mehsulData.sekil}" alt="${mehsulData.adi}" class="product-image-image-tr">` 
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
            
            .product-image-image-tr {
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
    document.addEventListener('DOMContentLoaded', function() {
        try {
            console.log('DOM yükləndi, funksiyalar başladılır...'); // Debug üçün
            
            // Global funksiyaları window obyektinə əlavə et
            window.selectUser = selectUser;
            window.confirmLogout = confirmLogout;
            
            // Saatı başlat
            updateCurrentTime();
            setInterval(updateCurrentTime, 1000);

            // İş saatlarını yoxla
            checkWorkingHours();
            setInterval(checkWorkingHours, 60000); // Hər dəqiqə yoxla

            // Səbət sayını yenilə
            updateCartCount();

            // Swiper-ləri inicializasiya et
            if (document.querySelector('.brandsSwiper')) {
                try {
                    new Swiper('.brandsSwiper', swiperConfig);
                } catch (error) {
                    console.error('Swiper inicializasiya xətası:', error);
                }
            }
            if (document.querySelector('.carBrandsSwiper')) {
                try {
                    new Swiper('.carBrandsSwiper', {
                        ...swiperConfig,
                        autoplay: {
                            ...swiperConfig.autoplay,
                            delay: 3500
                        }
                    });
                } catch (error) {
                    console.error('Swiper inicializasiya xətası:', error);
                }
            }

            // İlkin statistikaları yüklə
            if (document.querySelector('.statistics-card')) {
                updateStatistics();
                setInterval(updateStatistics, 3600000); // 1 saatdan bir yenilə
            }

            // Chat-i inicializasiya et
            if (document.getElementById('chat-widget')) {
                console.log('Chat widget tapıldı, inicializasiya edilir...'); // Debug üçün
                initChat();
            } else {
                console.log('Chat widget tapılmadı!'); // Debug üçün
            }

            // Rəy formu
            const reviewForm = document.querySelector('.review-form form');
            if (reviewForm) {
                reviewForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const rating = reviewForm.querySelector('input[name="qiymetlendirme"]:checked');
                    if (!rating) {
                        showReviewNotification('error', 'Zəhmət olmasa, qiymətləndirmə üçün ulduz seçin');
                        return;
                    }

                    const review = reviewForm.querySelector('textarea[name="rey"]').value.trim();
                    if (!review) {
                        showReviewNotification('error', 'Zəhmət olmasa, rəyinizi yazın');
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
                            showReviewNotification('success', 'Rəyiniz uğurla göndərildi. Təsdiqlənməsi gözlənilir');
                            reviewForm.reset();
                            setTimeout(() => {
                                window.location.reload();
                            }, 3000);
                        } else {
                            showReviewNotification('error', data.message || 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin');
                        }
                    })
                    .catch(error => {
                        console.error('Xəta:', error);
                        showReviewNotification('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin');
                    });
                });
            }

            // Çıxış funksiyası
            document.addEventListener('click', function(e) {
                if (e.target.closest('.logout-link')) {
                    confirmLogout(e);
                }
            });

            // Səbətə məhsul əlavə etmək
            const cartLinks = document.querySelectorAll('.cart-icon');
            if (cartLinks.length > 0) {
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
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error('Network response was not ok');
                                    }
                                    return response.json();
                                })
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
                                    this.innerHTML = originalContent;
                                    this.style.pointerEvents = 'auto';
                                    this.style.opacity = '1';
                                });
                        }, 2000);
                    });
                });
            }

            // Axtarış formu
            const searchForm = document.getElementById('search-form');
            if (searchForm) {
                searchForm.addEventListener('submit', function(event) {
                    event.preventDefault(); // Formun dərhal göndərilməsini dayandır
                
                    let searchButton = document.getElementById('search-button');
                    let spinner = document.getElementById('loading-spinner');
                
                    if (!searchButton || !spinner) return;
                
                    // Butonun ölçüsünü qorumaq üçün enini və hündürlüyünü sabit saxla
                    searchButton.style.width = `${searchButton.offsetWidth}px`;
                    searchButton.style.height = `${searchButton.offsetHeight}px`;
                    
                    // Axtarış yazısını gizlət, amma spinneri saxla
                    if (searchButton.childNodes[0] && searchButton.childNodes[0].nodeValue) {
                        searchButton.childNodes[0].nodeValue = ''; // Axtar sözünü sil
                    }
                    spinner.style.display = 'inline-block'; // Spinneri göstər
                
                    // Butonu deaktiv et ki, yenidən klik olunmasın
                    searchButton.disabled = true; 
                
                    // 2 saniyə sonra formu göndər
                    setTimeout(() => {
                        this.submit(); // Formu göndər
                    }, 2000);
                });
            }

        } catch (error) {
            console.error('Funksiya xətası:', error);
        }
    });

    function confirmLogout(event) {
        event.preventDefault();  // Default davranışı dayandırır
        if (confirm("Çıxış etmək istədiyinizə əminsiniz?")) {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // CSRF token-i al
            fetch(event.target.href, {  // URL burada event.target.href-dən alınır
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken  // CSRF token-i burada göndər
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

    // Sifariş funksiyaları
    function confirmOrder() {
        const modal = document.getElementById('confirmModal');
        modal.style.display = 'flex';
    }

    function closeModal() {
        const modal = document.getElementById('confirmModal');
        modal.style.display = 'none';
    }

    function submitOrder() {
        const submitButton = document.querySelector('.confirm-btn');
        const originalContent = submitButton.innerHTML;
        
        // Loading effekti
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Göndərilir...';
        submitButton.disabled = true;

        fetch('/submit_order/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Təsdiq modalını bağla
                document.getElementById('confirmModal').style.display = 'none';
                
                // Uğurlu sifariş modalını göstər
                const successModal = document.getElementById('successModal');
                successModal.style.display = 'flex';
                
                // 3 saniyə sonra yönləndir
                setTimeout(() => {
                    window.location.href = '/sifaris_izle/';
                }, 3000);
            } else {
                showAnimatedMessage(data.error || "Sifariş zamanı xəta baş verdi", true);
                submitButton.innerHTML = originalContent;
                submitButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Xəta:', error);
            showAnimatedMessage("Server xətası baş verdi", true);
            submitButton.innerHTML = originalContent;
            submitButton.disabled = false;
        });
    }

    // Səbət funksiyaları
    function updateQuantity(itemId, change) {
        const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
        const input = row.querySelector('.quantity-input');
        const currentValue = parseInt(input.value);
        
        let newValue;
        if (typeof change === 'number') {
            newValue = currentValue + change;
        } else {
            newValue = parseInt(change);
        }

        if (newValue < 1) newValue = 1;

        const price = parseFloat(row.getAttribute('data-price'));
        
        fetch(`/update_cart/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quantity: newValue
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                input.value = newValue;
                row.querySelector('.item-total').textContent = `${(price * newValue).toFixed(2)} AZN`;
                document.getElementById('total-amount').textContent = `${data.total} AZN`;
                updateCartCount();
            } else {
                showAnimatedMessage(data.error || "Miqdar yeniləmə xətası", true);
            }
        })
        .catch(error => {
            console.error('Xəta:', error);
            showAnimatedMessage("Server xətası baş verdi", true);
        });
    }

    function removeItem(itemId) {
        if (confirm('Bu məhsulu səbətdən silmək istədiyinizə əminsiniz?')) {
            fetch(`/remove_from_cart/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
                    row.remove();
                    document.getElementById('total-amount').textContent = `${data.total} AZN`;
                    updateCartCount();
                    
                    // Səbət boşdursa, boş səbət mesajını göstər
                    if (data.is_empty) {
                        location.reload();
                    }
                } else {
                    showAnimatedMessage(data.error || "Silmə xətası baş verdi", true);
                }
            })
            .catch(error => {
                console.error('Xəta:', error);
                showAnimatedMessage("Server xətası baş verdi", true);
            });
        }
    }

    // Modal bağlama
    window.onclick = function(event) {
        const confirmModal = document.getElementById('confirmModal');
        const successModal = document.getElementById('successModal');
        if (event.target === confirmModal) {
            confirmModal.style.display = 'none';
        }
        if (event.target === successModal) {
            successModal.style.display = 'none';
        }
    }

    // Bildiriş göstərmə funksiyası
    window.showNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 15px;
            border-radius: 4px;
            z-index: 1000;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    };

    // Miqdar dəyişikliyi üçün debounce funksiyası
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Miqdar dəyişikliyi
    window.handleQuantityInput = debounce(function(input) {
        const value = parseInt(input.value);
        const itemId = input.dataset.itemId;
        
        if (!isNaN(value) && value > 0) {
            updateQuantity(itemId, 'set', value);
        } else {
            input.value = 1;
            updateQuantity(itemId, 'set', 1);
        }
    }, 300);

    // Miqdar yeniləmə funksiyası
    window.updateQuantity = function(itemId, value) {
        const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
        const input = row.querySelector('.quantity-input');
        let newQuantity;

        if (typeof value === 'number') {
            newQuantity = parseInt(input.value) + value;
        } else if (value === 'set') {
            newQuantity = parseInt(input.value);
        } else {
            newQuantity = parseInt(value);
        }

        if (isNaN(newQuantity) || newQuantity < 1) {
            newQuantity = 1;
        }

        // Düyməni deaktiv et və loading göstər
        const buttons = row.querySelectorAll('.quantity-btn');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.5';
        });
        input.disabled = true;

        // Loading ikonunu göstər
        const loadingIcon = document.createElement('span');
        loadingIcon.className = 'loading-icon';
        loadingIcon.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        input.parentNode.appendChild(loadingIcon);

        fetch(`/update_quantity/${itemId}/${newQuantity}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    input.value = data.new_quantity;
                    const itemTotalElement = row.querySelector('.item-total');
                    itemTotalElement.textContent = data.item_total.toFixed(2) + ' AZN';
                    
                    const totalElement = document.getElementById('total-amount');
                    if (totalElement) {
                        totalElement.textContent = data.total_amount.toFixed(2) + ' AZN';
                        totalElement.classList.add('highlight');
                        setTimeout(() => totalElement.classList.remove('highlight'), 300);
                    }

                    row.classList.add('highlight');
                    setTimeout(() => row.classList.remove('highlight'), 300);
                } else {
                    input.value = input.defaultValue;
                    window.showNotification(data.error || 'Xəta baş verdi', 'error');
                }
            })
            .catch(error => {
                console.error('Xəta:', error);
                input.value = input.defaultValue;
                window.showNotification('Xəta baş verdi', 'error');
            })
            .finally(() => {
                // Düymələri və inputu yenidən aktiv et
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
                input.disabled = false;
                
                // Loading ikonunu sil
                const loadingIcon = row.querySelector('.loading-icon');
                if (loadingIcon) {
                    loadingIcon.remove();
                }
            });
    };

    // CSS stilləri
    const cartStyles = document.createElement('style');
    cartStyles.textContent = `
        .highlight {
            animation: highlight 0.3s ease;
        }

        @keyframes highlight {
            0% {
                background-color: transparent;
            }
            50% {
                background-color: rgba(100, 255, 218, 0.2);
            }
            100% {
                background-color: transparent;
            }
        }
    `;
    document.head.appendChild(cartStyles);

    // Real-time search functionality
    document.addEventListener('DOMContentLoaded', function() {
        const searchForm = document.getElementById('search-form');
        const searchInput = searchForm.querySelector('input[name="search_text"]');
        const categorySelect = document.getElementById('category');
        const brandSelect = document.getElementById('brand');
        const modelSelect = document.getElementById('model');
        
        // Create dropdown container
        const dropdownContainer = document.createElement('div');
        dropdownContainer.className = 'search-results-dropdown';
        searchForm.appendChild(dropdownContainer);
        
        let searchTimeout;
        
        // Function to perform search
        async function performSearch() {
            const query = searchInput.value.trim();
            const category = categorySelect.value;
            const brand = brandSelect.value;
            const model = modelSelect.value;
            
            if (query.length < 2 && !category && !brand && !model) {
                dropdownContainer.classList.remove('active');
                return;
            }
            
            try {
                const response = await fetch(`/realtime-search/?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&brand=${encodeURIComponent(brand)}&model=${encodeURIComponent(model)}`);
                const data = await response.json();
                
                if (data.results.length > 0) {
                    dropdownContainer.innerHTML = data.results.map(result => {
                        const highlightTerm = (text, term) => {
                            const regex = new RegExp(`(${term})`, 'gi');
                            return text.replace(regex, '<span class="highlight">$1</span>');
                        };
                        return `
                            <div class="search-result-item" onclick="window.location.href='/product-detail/${encodeURIComponent(result.adi)}-${encodeURIComponent(result.oem)}-${encodeURIComponent(result.brend_kod)}/${result.id}/'">
                                ${result.sekil_url ? `<img src="${result.sekil_url}" alt="${result.adi}">` : ''}
                                <div class="search-result-info">
                                    <h4>${highlightTerm(result.adi, query)}</h4>
                                    <p>Brend: ${highlightTerm(result.brend, query)} | OEM: ${highlightTerm(result.oem, query)}</p>
                                    <p>Marka: ${highlightTerm(result.marka, query)} | Brend Kod: ${highlightTerm(result.brend_kod, query)}</p>
                                </div>
                                <div class="search-result-price">
                                    <div class="stock-status ${result.stok === 0 ? 'out-of-stock' : result.stok <= 20 ? 'low-stock' : 'in-stock'}">
                                        ${result.stok === 0 ? 'Yoxdur' : result.stok <= 20 ? 'Az var' : 'Var'}
                                    </div>
                                    ${result.qiymet} AZN
                                </div>
                            </div>
                        `;
                    }).join('');
                    dropdownContainer.classList.add('active');
                } else {
                    dropdownContainer.innerHTML = '<div class="search-result-item">Heç bir nəticə tapılmadı</div>';
                    dropdownContainer.classList.add('active');
                }
            } catch (error) {
                console.error('Axtarış xətası:', error);
            }
        }
        
        // Input event listener with debounce
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(performSearch, 300);
        });
        
        // Select elements change listener
        [categorySelect, brandSelect, modelSelect].forEach(select => {
            select.addEventListener('change', performSearch);
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchForm.contains(e.target)) {
                dropdownContainer.classList.remove('active');
            }
        });
        
        // Form submit handler
        searchForm.addEventListener('submit', (e) => {
            if (dropdownContainer.classList.contains('active')) {
                e.preventDefault();
                dropdownContainer.classList.remove('active');
            }
        });
    });

    function highlightSearchTerm(text, searchTerm) {
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    }

    // Profile Dropdown functionality
    document.addEventListener('DOMContentLoaded', function() {
        const profileDropdown = document.querySelector('.profile-dropdown');
        const profileToggle = document.querySelector('.profile-toggle');

        if (profileToggle && profileDropdown) {
            // Click handler for toggle button
            profileToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                profileDropdown.classList.toggle('active');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!profileDropdown.contains(e.target)) {
                    profileDropdown.classList.remove('active');
                }
            });

            // Close dropdown with ESC key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && profileDropdown.classList.contains('active')) {
                    profileDropdown.classList.remove('active');
                }
            });

            // Prevent dropdown from closing when clicking inside
            const dropdownMenu = profileDropdown.querySelector('.dropdown-menu');
            if (dropdownMenu) {
                dropdownMenu.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        }
    });

    function addToCartWithQuantity(productId) {
        const quantityInput = document.querySelector(`input[data-product-id="${productId}"]`);
        const quantity = parseInt(quantityInput.value);

        if (isNaN(quantity) || quantity <= 0) {
            showAnimatedMessage('Zəhmət olmasa düzgün miqdar daxil edin', true);
            return;
        }

        if (quantity > 999) {
            showAnimatedMessage('Maksimum 999 ədəd sifariş edə bilərsiniz', true);
            return;
        }

        fetch(`/sebet/ekle/${productId}/?miqdar=${quantity}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAnimatedMessage(`${data.mehsul.adi} səbətə əlavə edildi (${quantity} ədəd)`, false, data.mehsul);
                updateCartCount();
            } else {
                showAnimatedMessage(data.error || 'Xəta baş verdi', true);
            }
        })
        .catch(error => {
            showAnimatedMessage('Xəta baş verdi', true);
            console.error('Error:', error);
        });
    }

    function validateQuantity(input) {
        const value = parseInt(input.value);
        const errorDiv = input.parentElement.querySelector('.quantity-error');
        
        if (isNaN(value) || value < 1) {
            input.value = 1;
            errorDiv.textContent = 'Minimum miqdar 1 olmalıdır';
            errorDiv.classList.add('show');
            setTimeout(() => errorDiv.classList.remove('show'), 3000);
        } else if (value > 999) {
            input.value = 999;
            errorDiv.textContent = 'Maksimum miqdar 999 olmalıdır';
            errorDiv.classList.add('show');
            setTimeout(() => errorDiv.classList.remove('show'), 3000);
        }
    }

    function incrementQuantity(productId) {
        const input = document.querySelector(`input[data-product-id="${productId}"]`);
        const currentValue = parseInt(input.value);
        if (currentValue < 999) {
            input.value = currentValue + 1;
            validateQuantity(input);
        }
    }

    function decrementQuantity(productId) {
        const input = document.querySelector(`input[data-product-id="${productId}"]`);
        const currentValue = parseInt(input.value);
        if (currentValue > 1) {
            input.value = currentValue - 1;
            validateQuantity(input);
        }
    }

    function validateCartQuantity(input) {
        const value = parseInt(input.value);
        
        if (isNaN(value) || value < 1) {
            input.value = 1;
            showAnimatedMessage('Minimum miqdar 1 olmalıdır', true);
            handleQuantityInput(input);
        } else if (value > 999) {
            input.value = 999;
            showAnimatedMessage('Maksimum miqdar 999 olmalıdır', true);
            handleQuantityInput(input);
        } else {
            handleQuantityInput(input);
        }
    }

    // Chat funksionallığı
    let currentReceiverId = null;
    let currentReceiverName = null;
    let lastMessageCount = 0;
    let lastMessageId = 0;
    let chatSocket = null;

    // Yeni mesaj bildirişi səsi
    function playNewMessageSound() {
        const audio = document.getElementById('new-message-sound');
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(error => {
                console.log('Səs oxutma xətası:', error);
            });
        }
    }

    // Chat mesajı bildirişi səsi
    function playChatMessageSound() {
        const audio = document.getElementById('chat-message-sound');
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(error => {
                console.log('Səs oxutma xətası:', error);
            });
        }
    }

    function initChat() {
        console.log('Chat funksiyası başladılır...'); // Debug üçün
        
        // İstifadəçi daxil olmayıbsa, funksiyadan çıx
        if (typeof currentUserId === 'undefined' || !currentUserId) {
            console.log('İstifadəçi daxil olmayıb, chat funksiyası başladılmır');
            return;
        }
        
        const chatIcon = document.getElementById('chat-icon');
        const chatWindow = document.getElementById('chat-window');
        const closeChat = document.getElementById('close-chat');
        const backButton = document.getElementById('back-to-users');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-message');
        const chatMain = document.querySelector('.chat-main');
        const chatSidebar = document.querySelector('.chat-sidebar');

        if (!chatIcon || !chatWindow) {
            console.log('Chat elementləri tapılmadı!'); // Debug üçün
            return;
        }

        // WebSocket bağlantısını yarat
        connectWebSocket();

        // Chat ikonuna klik
        chatIcon.addEventListener('click', () => {
            chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
            if (chatWindow.style.display === 'flex') {
                loadChatUsers();
                chatMain.style.display = 'none';
                chatSidebar.style.display = 'block';
            }
        });

        // Chat pəncərəsini bağla
        closeChat.addEventListener('click', () => {
            chatWindow.style.display = 'none';
        });

        // İstifadəçilər siyahısına qayıt
        backButton.addEventListener('click', () => {
            chatMain.style.display = 'none';
            chatSidebar.style.display = 'block';
            currentReceiverId = null;
            currentReceiverName = null;
        });

        // Mesaj göndər
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // İstifadəçiləri və mesajları yenilə
        setInterval(loadChatUsers, 3000);
        setInterval(() => {
            if (currentReceiverId) {
                loadMessages(currentReceiverId);
            }
        }, 1000);

        // Axtarış funksiyasını əlavə et
        const searchInput = document.getElementById('user-search');
        if (searchInput) {
            searchInput.addEventListener('input', filterUsers);
        }
    }

    // WebSocket bağlantısını yarat
    function connectWebSocket() {
        console.log('WebSocket bağlantısı yaradılır...'); // Debug üçün
        
        try {
            // WebSocket bağlantısını yarat
            // Əgər WebSocket bağlantısı uğursuz olursa, HTTP sorğularından istifadə et
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${wsProtocol}//${window.location.host}/ws/chat/`;
            
            console.log('WebSocket URL:', wsUrl); // Debug üçün
            
            // Əvvəlki bağlantını bağla
            if (chatSocket && chatSocket.readyState !== WebSocket.CLOSED) {
                chatSocket.close();
            }
            
            try {
                chatSocket = new WebSocket(wsUrl);
                
                chatSocket.onopen = function(e) {
                    console.log('WebSocket bağlantısı açıldı');
                };
                
                chatSocket.onmessage = function(e) {
                    try {
                        const data = JSON.parse(e.data);
                        console.log('WebSocket mesajı alındı:', data);
                        
                        if (data.message) {
                            // Əgər hazırda həmin istifadəçi ilə söhbət edirsinizsə, mesajı göstər
                            if (currentReceiverId && (data.message.sender === currentReceiverName || data.message.is_mine)) {
                                appendMessage(data.message);
                                
                                // Əgər mesaj bizim deyilsə, səs çal
                                if (!data.message.is_mine) {
                                    playChatMessageSound();
                                }
                            } else {
                                // Əks halda bildiriş səsini çal
                                playNewMessageSound();
                                
                                // İstifadəçi siyahısını yenilə
                                loadChatUsers();
                            }
                        }
                    } catch (error) {
                        console.error('WebSocket mesajı işlənərkən xəta:', error);
                    }
                };
                
                chatSocket.onclose = function(e) {
                    console.log('WebSocket bağlantısı bağlandı', e.code, e.reason);
                    
                    // WebSocket bağlantısı uğursuz olduqda HTTP sorğularından istifadə et
                    console.log('WebSocket bağlantısı uğursuz oldu, HTTP sorğularından istifadə ediləcək');
                };
                
                chatSocket.onerror = function(e) {
                    console.error('WebSocket xətası:', e);
                    console.log('WebSocket bağlantısı uğursuz oldu, HTTP sorğularından istifadə ediləcək');
                };
            } catch (error) {
                console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
                console.log('WebSocket bağlantısı uğursuz oldu, HTTP sorğularından istifadə ediləcək');
            }
        } catch (error) {
            console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
        }
    }

    // Mesajı əlavə et
    function appendMessage(message) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        
        messageDiv.innerHTML = `
            ${!message.is_mine ? `<div class="message-sender">${message.sender}</div>` : ''}
            <div class="message-content">${message.content}</div>
            ${message.is_mine ? `
                <div class="message-status ${getMessageStatus(message)}">
                    ${getStatusIcons(message)}
                </div>
            ` : ''}
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Chat istifadəçilərini yükləmə funksiyası
    function loadChatUsers() {
        console.log('İstifadəçilər yüklənir...'); // Debug üçün
        
        // Əgər istifadəçi daxil olmayıbsa, funksiyadan çıx
        if (!currentUserId) {
            console.log('İstifadəçi daxil olmayıb, istifadəçilər yüklənmir');
            return;
        }
        
        fetch('/istifadeciler/api/chat/users/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 500) {
                    console.error('Server xətası (500): İstifadəçilər yüklənə bilmədi');
                } else if (response.status === 403) {
                    console.error('Giriş icazəsi yoxdur (403): İstifadəçi daxil olmayıb və ya sessiyanın vaxtı bitib');
                } else {
                    console.error(`HTTP xətası: ${response.status}`);
                }
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('İstifadəçi məlumatları alındı:', data); // Debug üçün
            
            const usersList = document.getElementById('users-list');
            if (!usersList) {
                console.error('users-list elementi tapılmadı!');
                return;
            }
            
            let totalUnread = 0;
            
            usersList.innerHTML = '';
            
            // Adminləri və istifadəçiləri əlavə et
            if (data.admins && data.admins.length > 0) {
                usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
                data.admins.forEach(user => {
                    totalUnread += user.unread_count;
                    usersList.innerHTML += createUserItem(user);
                });
            }
            
            if (data.users && data.users.length > 0) {
                usersList.innerHTML += '<div class="user-group-title">İstifadəçilər</div>';
                data.users.forEach(user => {
                    totalUnread += user.unread_count;
                    usersList.innerHTML += createUserItem(user);
                });
            }

            // Yeni mesaj varsa bildiriş səsini çal
            if (totalUnread > lastMessageCount) {
                playNewMessageSound();
            }

            lastMessageCount = totalUnread;
            updateUnreadCount(totalUnread);
        })
        .catch(error => {
            console.error('İstifadəçilər yüklənərkən xəta:', error);
        });
    }

    function createUserItem(user) {
        return `
            <div class="user-item ${user.unread_count > 0 ? 'has-unread' : ''}" 
                 onclick="selectUser(${user.id}, '${user.username}')">
                <div class="user-info">
                    <i class="fas ${user.is_admin ? 'fa-user-shield admin-icon' : 'fa-user'}"></i>
                    <span>${user.username}</span>
                </div>
                ${user.unread_count > 0 ? 
                    `<span class="unread-count">${user.unread_count}</span>` : 
                    ''}
            </div>
        `;
    }

    function updateUnreadCount(totalUnread) {
        const totalUnreadElement = document.getElementById('total-unread');
        const chatIcon = document.getElementById('chat-icon');
        
        if (!totalUnreadElement || !chatIcon) return;
        
        if (totalUnread > 0) {
            totalUnreadElement.textContent = totalUnread;
            totalUnreadElement.style.display = 'block';
            chatIcon.classList.add('has-notification');
        } else {
            totalUnreadElement.style.display = 'none';
            chatIcon.classList.remove('has-notification');
        }
    }

    function selectUser(userId, username) {
        console.log(`İstifadəçi seçildi: ${username} (ID: ${userId})`); // Debug üçün
        
        currentReceiverId = userId;
        currentReceiverName = username;
        
        const chatMain = document.querySelector('.chat-main');
        const chatSidebar = document.querySelector('.chat-sidebar');
        const selectedUsername = document.getElementById('selected-username');
        
        if (!chatMain || !chatSidebar || !selectedUsername) {
            console.error('Chat elementləri tapılmadı!');
            return;
        }
        
        chatSidebar.style.display = 'none';
        chatMain.style.display = 'flex';
        selectedUsername.textContent = username;
        
        loadMessages(userId);
    }

    // Mesaj yükləmə funksiyası
    function loadMessages(receiverId) {
        console.log(`${receiverId} ID-li istifadəçi ilə mesajlar yüklənir...`); // Debug üçün
        
        fetch(`/istifadeciler/api/chat/messages/${receiverId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(messages => {
                console.log(`${messages.length} mesaj alındı`); // Debug üçün
                
                const chatMessages = document.getElementById('chat-messages');
                if (!chatMessages) {
                    console.error('chat-messages elementi tapılmadı!');
                    return;
                }
                
                // Son mesajın ID-sini al
                const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
                
                // HTML-i yenilə
                chatMessages.innerHTML = messages.map(msg => `
                    <div class="message ${msg.is_mine ? 'mine' : 'theirs'}">
                        ${!msg.is_mine ? `<div class="message-sender">${msg.sender}</div>` : ''}
                        <div class="message-content">${msg.content}</div>
                        ${msg.is_mine ? `
                            <div class="message-status ${getMessageStatus(msg)}">
                                ${getStatusIcons(msg)}
                            </div>
                        ` : ''}
                    </div>
                `).join('');

                // Yeni mesaj gəlibsə və bu mesaj bizim deyilsə səs çal
                if (lastMessage && lastMessage.id > lastMessageId && !lastMessage.is_mine) {
                    playChatMessageSound();
                }

                // Son mesaj ID-sini yadda saxla
                if (lastMessage) {
                    lastMessageId = lastMessage.id;
                }
                
                // Mesajları aşağı sürüşdür
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                console.error('Mesajlar yüklənərkən xəta:', error);
            });
    }

    // Mesaj statusunu müəyyən et
    function getMessageStatus(msg) {
        if (msg.is_read) return 'read';
        if (msg.is_delivered) return 'delivered';
        return 'sent';
    }

    // Status ikonlarını qaytarır
    function getStatusIcons(msg) {
        if (msg.is_read) {
            return '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
        } else if (msg.is_delivered) {
            return '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
        } else {
            return '<i class="fas fa-check"></i>';
        }
    }

    function sendMessage() {
        const input = document.getElementById('message-input');
        if (!input) return;
        
        const content = input.value.trim();
        
        if (!content || !currentReceiverId) return;

        console.log(`Mesaj göndərilir: ${content} (Alıcı ID: ${currentReceiverId})`); // Debug üçün

        // WebSocket ilə mesaj göndərməyə çalış
        let websocketSent = false;
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            try {
                chatSocket.send(JSON.stringify({
                    'message': content,
                    'sender': currentUserId,
                    'receiver': currentReceiverId
                }));
                websocketSent = true;
                console.log('Mesaj WebSocket ilə göndərildi');
            } catch (error) {
                console.error('WebSocket ilə mesaj göndərilərkən xəta:', error);
            }
        }

        // HTTP sorğusu ilə mesaj göndər (WebSocket uğursuz olduqda və ya hər halda)
        const formData = new FormData();
        formData.append('receiver_id', currentReceiverId);
        formData.append('content', content);

        fetch('/istifadeciler/api/chat/send/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Mesaj göndərildi:', data); // Debug üçün
            
            if (data.status === 'success') {
                input.value = '';
                
                // Əgər WebSocket ilə göndərilməyibsə, mesajları yenilə
                if (!websocketSent) {
                    loadMessages(currentReceiverId);
                }
            } else {
                console.error('Mesaj göndərilə bilmədi:', data.message);
            }
        })
        .catch(error => {
            console.error('Mesaj göndərilərkən xəta:', error);
        });
    }

    function filterUsers() {
        const searchTerm = document.getElementById('user-search').value.toLowerCase();
        const userItems = document.querySelectorAll('.user-item');
        const userGroupTitles = document.querySelectorAll('.user-group-title');
        
        // Əgər axtarış boşdursa hər şeyi göstər
        if (!searchTerm) {
            userGroupTitles.forEach(title => {
                title.style.display = 'block';
            });
            userItems.forEach(item => {
                item.style.display = 'flex';
            });
            return;
        }

        // Əvvəlcə bütün başlıqları və istifadəçiləri gizlət
        userGroupTitles.forEach(title => {
            title.style.display = 'none';
        });
        userItems.forEach(item => {
            item.style.display = 'none';
        });

        // Axtarış sözünə uyğun istifadəçiləri göstər
        let adminFound = false;
        let userFound = false;

        userItems.forEach(item => {
            const username = item.querySelector('.user-info span').textContent.toLowerCase();
            if (username.includes(searchTerm)) {
                item.style.display = 'flex';
                // İstifadəçinin admin olub-olmadığını yoxla
                const isAdmin = item.querySelector('.admin-icon') !== null;
                if (isAdmin) {
                    adminFound = true;
                    document.querySelector('.user-group-title:first-of-type').style.display = 'block';
                } else {
                    userFound = true;
                    document.querySelector('.user-group-title:last-of-type').style.display = 'block';
                }
            }
        });
    }

    // Səhifə yükləndikdə istifadəçi qarşılıqlı əlaqəsini gözlə
    document.addEventListener('click', function initAudioOnUserInteraction() {
        initAudio();
        document.removeEventListener('click', initAudioOnUserInteraction);
    }, { once: true });

    // Audio elementlərini inicializasiya et
    function initAudio() {
        const newMessageSound = document.getElementById('new-message-sound');
        const chatMessageSound = document.getElementById('chat-message-sound');
        
        if (newMessageSound) {
            newMessageSound.load();
        }
        
        if (chatMessageSound) {
            chatMessageSound.load();
        }
    }

    // CSS stilləri əlavə et
    const chatStyles = document.createElement('style');
    chatStyles.textContent = `
        /* Chat Widget Stilləri */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }

        .chat-icon {
            width: 60px;
            height: 60px;
            background-color: #003366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            position: relative;
            transition: all 0.3s ease;
        }

        .chat-icon i {
            color: white;
            font-size: 24px;
        }

        .chat-icon:hover {
            transform: scale(1.1);
        }

        .chat-icon.has-notification {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 51, 102, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(0, 51, 102, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 51, 102, 0); }
        }

        .unread-count {
            position: absolute;
            top: -5px;
            right: -5px;
            background-color: #ff5252;
            color: white;
            border-radius: 50%;
            width: 22px;
            height: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }

        .chat-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
        }

        .chat-header {
            background-color: #003366;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-title {
            font-weight: bold;
            font-size: 16px;
        }

        .close-button {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
        }

        .chat-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        .chat-sidebar {
            width: 100%;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #eee;
        }

        .search-box {
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
        }

        .search-box i {
            color: #999;
            margin-right: 10px;
        }

        .search-box input {
            border: none;
            outline: none;
            width: 100%;
            padding: 5px;
        }

        .users-list {
            flex: 1;
            overflow-y: auto;
        }

        .user-group-title {
            padding: 10px;
            background-color: #f5f5f5;
            font-weight: bold;
            font-size: 14px;
            color: #666;
        }

        .user-item {
            padding: 12px 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s;
        }

        .user-item:hover {
            background-color: #f9f9f9;
        }

        .user-item.has-unread {
            background-color: rgba(0, 51, 102, 0.05);
        }

        .user-info {
            display: flex;
            align-items: center;
        }

        .user-info i {
            margin-right: 10px;
            color: #003366;
        }

        .admin-icon {
            color: #ff9800 !important;
        }

        .chat-main {
            width: 100%;
            display: flex;
            flex-direction: column;
        }

        .selected-user {
            padding: 12px 15px;
            background-color: #f5f5f5;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #eee;
        }

        .selected-user i {
            margin-right: 15px;
            cursor: pointer;
            color: #003366;
        }

        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background-color: #f9f9f9;
        }

        .message {
            margin-bottom: 15px;
            max-width: 80%;
            position: relative;
        }

        .message.mine {
            margin-left: auto;
            background-color: #e1f5fe;
            border-radius: 15px 15px 0 15px;
            padding: 10px 15px;
        }

        .message.theirs {
            margin-right: auto;
            background-color: white;
            border-radius: 15px 15px 15px 0;
            padding: 10px 15px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .message-sender {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }

        .message-content {
            word-break: break-word;
        }

        .message-status {
            font-size: 10px;
            color: #999;
            text-align: right;
            margin-top: 5px;
        }

        .message-status.read {
            color: #4caf50;
        }

        .chat-input {
            padding: 10px;
            display: flex;
            align-items: center;
            border-top: 1px solid #eee;
        }

        .chat-input input {
            flex: 1;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 8px 15px;
            outline: none;
        }

        .chat-input button {
            background-color: #003366;
            color: white;
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            margin-left: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;
        }

        .chat-input button:hover {
            background-color: #002244;
        }
    `;

    document.head.appendChild(chatStyles);