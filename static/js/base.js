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

            // İlkin statistikaları yüklə1
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
    const chatHtml = `
        <div id="chat-widget" class="chat-widget">
            <div class="chat-toggle" onclick="toggleChat()">
                <i class="fas fa-comments"></i>
                <span class="unread-count" style="display: none;">0</span>
            </div>
            <div class="chat-container" style="display: none;">
                <div class="chat-header">
                    <h3>Mesajlar</h3>
                    <button onclick="toggleChat()" class="close-chat">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="chat-users">
                    <!-- İstifadəçilər burada göstəriləcək -->
                </div>
                <div class="chat-messages" style="display: none;">
                    <div class="messages-header">
                        <button onclick="showUsers()" class="back-button">
                            <i class="fas fa-arrow-left"></i>
                        </button>
                        <h4 class="chat-user-name"></h4>
                    </div>
                    <div class="messages-container"></div>
                    <div class="message-input">
                        <textarea placeholder="Mesajınızı yazın..."></textarea>
                        <button onclick="sendMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Chat CSS
    const chatStyles = `
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            font-family: Arial, sans-serif;
        }

        .chat-toggle {
            width: 60px;
            height: 60px;
            background: #003366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            position: relative;
        }

        .chat-toggle i {
            color: white;
            font-size: 24px;
        }

        .unread-count {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ff4444;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }

        .chat-container {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 300px;
            height: 400px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 15px;
            background: #003366;
            color: white;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header h3 {
            margin: 0;
            font-size: 16px;
        }

        .close-chat {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 18px;
        }

        .chat-users {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }

        .user-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background-color 0.3s;
        }

        .user-item:hover {
            background-color: #f0f0f0;
        }

        .user-item.has-unread {
            background-color: #e3f2fd;
        }

        .chat-messages {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .messages-header {
            padding: 15px;
            background: #003366;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .back-button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .message {
            max-width: 80%;
            padding: 8px 12px;
            border-radius: 15px;
            margin: 2px 0;
        }

        .message.received {
            background-color: #f0f0f0;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }

        .message.sent {
            background-color: #003366;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }

        .message-time {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 4px;
        }

        .message-input {
            padding: 10px;
            display: flex;
            gap: 10px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }

        .message-input textarea {
            flex: 1;
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            resize: none;
            height: 40px;
            font-family: inherit;
        }

        .message-input button {
            background: #003366;
            color: white;
            border: none;
            border-radius: 5px;
            width: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .message-input button:hover {
            background: #002244;
        }
    `;

    // Chat funksiyaları
    let currentChatUser = null;
    let chatUpdateInterval = null;

    function initChat() {
        // CSS əlavə et
        const style = document.createElement('style');
        style.textContent = chatStyles;
        document.head.appendChild(style);

        // Chat HTML-i əlavə et
        document.body.insertAdjacentHTML('beforeend', chatHtml);

        // Enter düyməsi ilə mesaj göndərmə
        const textarea = document.querySelector('.message-input textarea');
        textarea.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // İstifadəçiləri yüklə
        loadUsers();

        // Oxunmamış mesajları yoxla
        updateUnreadCount();
        setInterval(updateUnreadCount, 5000);
    }

    function toggleChat() {
        const container = document.querySelector('.chat-container');
        container.style.display = container.style.display === 'none' ? 'flex' : 'none';
    }

    function showUsers() {
        document.querySelector('.chat-users').style.display = 'block';
        document.querySelector('.chat-messages').style.display = 'none';
        currentChatUser = null;
        if (chatUpdateInterval) {
            clearInterval(chatUpdateInterval);
        }
    }

    function loadUsers() {
        fetch('/chat/users/')
            .then(response => response.json())
            .then(data => {
                const usersContainer = document.querySelector('.chat-users');
                usersContainer.innerHTML = data.users.map(user => `
                    <div class="user-item ${user.unread_count > 0 ? 'has-unread' : ''}" 
                         onclick="openChat(${user.id}, '${user.username}')">
                        <span>${user.username}</span>
                        ${user.unread_count > 0 ? 
                            `<span class="unread-badge">${user.unread_count}</span>` : ''}
                    </div>
                `).join('');
            });
    }

    function openChat(userId, username) {
        currentChatUser = userId;
        document.querySelector('.chat-user-name').textContent = username;
        document.querySelector('.chat-users').style.display = 'none';
        document.querySelector('.chat-messages').style.display = 'flex';
        
        loadMessages();
        
        // Mesajları avtomatik yenilə
        if (chatUpdateInterval) {
            clearInterval(chatUpdateInterval);
        }
        chatUpdateInterval = setInterval(loadMessages, 3000);
    }

    function loadMessages() {
        if (!currentChatUser) return;
        
        fetch(`/chat/messages/?user_id=${currentChatUser}`)
            .then(response => response.json())
            .then(data => {
                const container = document.querySelector('.messages-container');
                container.innerHTML = data.messages.map(msg => `
                    <div class="message ${msg.is_mine ? 'sent' : 'received'}">
                        <div class="message-content">${msg.content}</div>
                        <div class="message-time">${msg.timestamp}</div>
                    </div>
                `).join('');
                container.scrollTop = container.scrollHeight;
                updateUnreadCount();
            });
    }

    function sendMessage() {
        if (!currentChatUser) return;
        
        const textarea = document.querySelector('.message-input textarea');
        const content = textarea.value.trim();
        
        if (!content) return;
        
        fetch('/chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                receiver_id: currentChatUser,
                content: content
            })
        })
        .then(response => response.json())
        .then(data => {
            textarea.value = '';
            loadMessages();
        })
        .catch(error => {
            console.error('Mesaj göndərmə xətası:', error);
            showAnimatedMessage('Mesaj göndərilə bilmədi', true);
        });
    }

    function updateUnreadCount() {
        fetch('/chat/unread-count/')
            .then(response => response.json())
            .then(data => {
                const unreadCount = document.querySelector('.unread-count');
                if (data.unread_count > 0) {
                    unreadCount.textContent = data.unread_count;
                    unreadCount.style.display = 'flex';
                } else {
                    unreadCount.style.display = 'none';
                }
            });
    }

    // Chat sistemini başlat
    document.addEventListener('DOMContentLoaded', function() {
        initChat();
    });