// Utility Functions
// -----------------

// CSRF token əldə etmə
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

// Debounce funksiyası (eyni funksiyanın tez-tez çağırılmasını limitlemək üçün)
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

// Universal bildiriş funksiyası
function showNotification(message, options = {}) {
    // Default options
    const defaults = {
        type: 'success',
        duration: 3000,
        position: 'top-right',
        productData: null,
        animationType: 'slide' // 'slide', 'fade', 'pop'
    };
    
    const settings = { ...defaults, ...options };
    const existingNotification = document.querySelector('.notification-container');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Notification container
    const notification = document.createElement('div');
    notification.className = `notification-container ${settings.type} ${settings.animationType}`;
    
    // Icon təyin etmə
    const icon = settings.type === 'success' ? 'check' : 'exclamation-circle';
    const title = settings.type === 'success' ? 'Uğurlu!' : 'Xəta!';
    
    // Notification content
    let contentHTML = `
        <div class="notification-content">
            <div class="icon">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
            <div class="progress">
                <div class="progress-bar"></div>
            </div>
        </div>
    `;
    
    // Məhsul məlumatları varsa, əlavə et
    if (settings.productData && settings.productData.adi) {
        contentHTML += `
            <div class="product-info">
                ${settings.productData.sekil ? 
                    `<img src="${settings.productData.sekil}" alt="${settings.productData.adi}" class="product-image-image-tr">` 
                    : ''
                }
                <span class="product-name">${settings.productData.adi}</span>
                ${settings.productData.oem ? `<span class="product-name">${settings.productData.oem}</span>` : ''}
            </div>
        `;
    }
    
    notification.innerHTML = contentHTML;
    
    // Position settings
    Object.assign(notification.style, {
        position: 'fixed',
        zIndex: '2000',
        minWidth: '300px',
        backgroundColor: settings.type === 'success' ? '#003366' : '#dc3545',
        color: '#ffffff',
        padding: '15px 25px',
        borderRadius: '8px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.15)',
        border: settings.type === 'success' ? '1px solid #eee' : 'none',
        transition: 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)'
    });
    
    // Pozisiyaya görə stil tənzimləmələri
    switch(settings.position) {
        case 'top-right':
            notification.style.top = '20px';
            notification.style.right = '-400px';
            break;
        case 'top-left':
            notification.style.top = '20px';
            notification.style.left = '-400px';
            break;
        case 'bottom-right':
            notification.style.bottom = '20px';
            notification.style.right = '-400px';
            break;
        case 'bottom-left':
            notification.style.bottom = '20px';
            notification.style.left = '-400px';
            break;
        case 'center':
            notification.style.top = '50%';
            notification.style.left = '50%';
            notification.style.transform = 'translate(-50%, -50%) scale(0.8)';
            notification.style.opacity = '0';
            break;
    }
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .notification-container {
            display: flex;
            flex-direction: column;
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .content {
            font-size: 1rem;
            font-weight: 500;
        }
        .icon {
            width: 30px;
            height: 30px;
            position: relative;
            border-radius: 50%;
            background-color: ${settings.type === 'success' ? '#4CAF50' : '#f44336'};
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .icon i {
            color: white;
            font-size: 16px;
        }
        .progress {
            width: 100%;
            height: 3px;
            background-color: rgba(255, 255, 255, 0.3);
            margin-top: 10px;
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            width: 100%;
            background-color: white;
            animation: progress-animation ${settings.duration}ms linear;
            transform-origin: left;
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
        @keyframes progress-animation {
            0% { transform: scaleX(1); }
            100% { transform: scaleX(0); }
        }
        @keyframes pop {
            0% { transform: scale(0) }
            50% { transform: scale(1.2) }
            100% { transform: scale(1) }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(notification);
    
    // Show notification with animation
    requestAnimationFrame(() => {
        if (settings.position.includes('right')) {
            notification.style.right = '20px';
        } else if (settings.position.includes('left')) {
            notification.style.left = '20px';
        } else if (settings.position === 'center') {
            notification.style.opacity = '1';
            notification.style.transform = 'translate(-50%, -50%) scale(1)';
        }
    });
    
    // Hide after duration
    setTimeout(() => {
        if (settings.position.includes('right')) {
            notification.style.right = '-400px';
        } else if (settings.position.includes('left')) {
            notification.style.left = '-400px';
        } else if (settings.position === 'center') {
            notification.style.opacity = '0';
            notification.style.transform = 'translate(-50%, -50%) scale(0.8)';
        }
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, settings.duration);
}

// Universal API istək göndərmə funksiyası
async function apiRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: null,
        successMessage: null,
        errorMessage: 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin',
        onSuccess: null,
        onError: null
    };
    
    const settings = { ...defaults, ...options };
    
    try {
        const response = await fetch(url, {
            method: settings.method,
            headers: settings.headers,
            body: settings.body ? JSON.stringify(settings.body) : null
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (settings.successMessage) {
                showNotification(settings.successMessage, { type: 'success' });
            }
            if (settings.onSuccess) {
                settings.onSuccess(data);
            }
            return data;
        } else {
            const message = data.error || data.message || settings.errorMessage;
            showNotification(message, { type: 'error' });
            if (settings.onError) {
                settings.onError(data);
            }
            return data;
        }
    } catch (error) {
        console.error('Xəta:', error);
        showNotification(settings.errorMessage, { type: 'error' });
        if (settings.onError) {
            settings.onError({ error: error.message });
        }
        return { success: false, error: error.message };
    }
}

// Sayğac animasiyası funksiyası
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

// Modal funksiyaları
function createModal(id, content, options = {}) {
    const defaults = {
        closable: true,
        width: '450px',
        onClose: null
    };
    
    const settings = { ...defaults, ...options };
    
    // Mövcud modal varsa sil
    const existingModal = document.getElementById(id);
    if (existingModal) {
        existingModal.remove();
    }
    
    // Yeni modal yarat
    const modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal';
    modal.style.cssText = `
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        justify-content: center;
        align-items: center;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.style.cssText = `
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        width: ${settings.width};
        max-width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
    `;
    
    if (settings.closable) {
        const closeBtn = document.createElement('button');
        closeBtn.className = 'modal-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        `;
        closeBtn.onclick = () => closeModal(id);
        modalContent.appendChild(closeBtn);
    }
    
    modalContent.appendChild(content);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Event listeners
    if (settings.closable) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(id);
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                closeModal(id);
            }
        });
    }
    
    return {
        open: () => openModal(id),
        close: () => closeModal(id)
    };
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        
        // onClose callback-i mövcuddursa çağır
        if (modal.onClose && typeof modal.onClose === 'function') {
            modal.onClose();
        }
    }
}

// Feature Functions
// ----------------

// Statistika yeniləmə
function updateStatistics() {
    apiRequest('/get_statistics/', {
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        },
        onSuccess: (data) => {
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
                        }, 8000);
                    }
                }
            });
        },
        onError: (error) => {
            console.error('Statistika yeniləmə xətası:', error);
            setTimeout(updateStatistics, 3600000); // 1 saatdan sonra yenidən cəhd et
        }
    });
}

// Səbət sayını yenilə
function updateCartCount() {
    apiRequest('/get_cart_count/', {
        onSuccess: (data) => {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.count;
            }
        }
    });
}

// Miqdar yeniləmə funksiyası
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
    
    apiRequest(`/update_cart/${itemId}/`, {
        method: 'POST',
        body: { quantity: newValue },
        onSuccess: (data) => {
            input.value = newValue;
            row.querySelector('.item-total').textContent = `${(price * newValue).toFixed(2)} AZN`;
            document.getElementById('total-amount').textContent = `${data.total} AZN`;
            updateCartCount();
            
            // Highlight effect
            row.classList.add('highlight');
            setTimeout(() => row.classList.remove('highlight'), 300);
        },
        onError: (data) => {
            input.value = currentValue; // Reset to original value
        },
        errorMessage: "Miqdar yeniləmə xətası"
    }).finally(() => {
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
}

// Məhsulu səbətdən sil
function removeItem(itemId) {
    if (confirm('Bu məhsulu səbətdən silmək istədiyinizə əminsiniz?')) {
        apiRequest(`/remove_from_cart/${itemId}/`, {
            method: 'POST',
            onSuccess: (data) => {
                const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
                row.remove();
                document.getElementById('total-amount').textContent = `${data.total} AZN`;
                updateCartCount();
                
                // Səbət boşdursa, boş səbət mesajını göstər
                if (data.is_empty) {
                    location.reload();
                }
            },
            errorMessage: "Silmə xətası baş verdi"
        });
    }
}

// Cari vaxtı yenilə
function updateCurrentTime() {
    const currentTimeElement = document.getElementById('current-time');
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

// İş saatlarını yoxla
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

// Sifarişi təsdiqlə
function submitOrder() {
    const submitButton = document.querySelector('.confirm-btn');
    const originalContent = submitButton.innerHTML;
    
    // Loading effekti
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Göndərilir...';
    submitButton.disabled = true;

    apiRequest('/submit_order/', {
        method: 'POST',
        onSuccess: (data) => {
            // Təsdiq modalını bağla
            closeModal('confirmModal');
            
            // Uğurlu sifariş modalını göstər
            openModal('successModal');
            
            // 3 saniyə sonra yönləndir
            setTimeout(() => {
                window.location.href = '/sifaris_izle/';
            }, 3000);
        },
        onError: () => {
            submitButton.innerHTML = originalContent;
            submitButton.disabled = false;
        },
        errorMessage: "Sifariş zamanı xəta baş verdi"
    });
}

// Real-time search
function performSearch(query, category, brand, model, dropdownContainer) {
    if (query.length < 2 && !category && !brand && !model) {
        dropdownContainer.classList.remove('active');
        return;
    }
    
    // URL parametrlərini hazırla
    const params = new URLSearchParams({
        q: query,
        category: category || '',
        brand: brand || '',
        model: model || ''
    });
    
    apiRequest(`/realtime-search/?${params.toString()}`, {
        onSuccess: (data) => {
            if (data.results.length > 0) {
                dropdownContainer.innerHTML = data.results.map(result => {
                    const highlightTerm = (text, term) => {
                        if (!term || term.length < 2) return text;
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
        }
    });
}

// DOM yükləndikdə icra olunacaq funksiyalar
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Global CSS stilləri əlavə et
        const globalStyles = document.createElement('style');
        globalStyles.textContent = `
            .highlight {
                animation: highlight 0.3s ease;
            }

            @keyframes highlight {
                0% { background-color: transparent; }
                50% { background-color: rgba(100, 255, 218, 0.2); }
                100% { background-color: transparent; }
            }
            
            /* Other global styles */
        `;
        document.head.appendChild(globalStyles);
        
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
                    apiRequest(url, {
                        onSuccess: (data) => {
                            showNotification("Məhsul səbətə əlavə olundu!", {
                                type: 'success',
                                productData: data.mehsul
                            });
                            updateCartCount();
                        },
                        onError: (data) => {
                            showNotification(
                                data.error || "Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.",
                                { type: 'error' }
                            );
                        },
                        errorMessage: "Serverdə xəta baş verdi."
                    }).finally(() => {
                        // Original ikonu bərpa et
                        this.innerHTML = originalContent;
                        this.style.pointerEvents = 'auto';
                        this.style.opacity = '1';
                    });
                }, 2000);
            });
        });

        // Swiper-ləri inicializasiya et
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
                320: { slidesPerView: 1, spaceBetween: 10 },
                480: { slidesPerView: 2, spaceBetween: 20 },
                768: { slidesPerView: 3, spaceBetween: 30 },
                1024: { slidesPerView: 4, spaceBetween: 40 }
            }
        };
        
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
                    showNotification('Zəhmət olmasa, qiymətləndirmə üçün ulduz seçin', { type: 'error' });
                    return;
                }

                const review = reviewForm.querySelector('textarea[name="rey"]').value.trim();
                if (!review) {
                    showNotification('Zəhmət olmasa, rəyinizi yazın', { type: 'error' });
                    return;
                }

                const formData = new FormData(reviewForm);
                
                apiRequest(reviewForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    onSuccess: () => {
                        showNotification('Rəyiniz uğurla göndərildi. Təsdiqlənməsi gözlənilir', { type: 'success' });
                        reviewForm.reset();
                        setTimeout(() => {
                            window.location.reload();
                        }, 3000);
                    },
                    errorMessage: 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin'
                });
            });
        }
    } catch (error) {
        console.error('Error loading content:', error);
    }
});

