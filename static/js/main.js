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

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Saatı başlat
        updateCurrentTime();
        setInterval(updateCurrentTime, 1000);

        // İş saatlarını yoxla
        checkWorkingHours();
        setInterval(checkWorkingHours, 60000); // Hər dəqiqə yoxla

    } catch (error) {
        console.error('Saat funksiyası xətası:', error);
    }
});

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

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', function() {
    // Swiper-ləri inicializasiya et
    new Swiper('.brandsSwiper', swiperConfig);
    new Swiper('.carBrandsSwiper', {
        ...swiperConfig,
        autoplay: {
            ...swiperConfig.autoplay,
            delay: 3500
        }
    });

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
                showReviewNotification('error', 'Zəhmət olmasa, qiymətləndirmə üçün ulduz seçin');
                return;
            }

            const review = reviewForm.querySelector('textarea[name="rey"]').value.trim();
            if (!review) {
                showReviewNotification('error', 'Zəhmət olmasa, rəyinizi yazın');
                return;
            }

            fetch(reviewForm.action, {
                method: 'POST',
                body: new FormData(reviewForm),
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showReviewNotification(
                        "Rəyiniz uğurla göndərildi. Təsdiqlənməsi gözlənilir.", 
                        false, 
                        data.mehsul
                    );
                    reviewForm.reset();
                } else {
                    showReviewNotification(
                        data.error || "Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.", 
                        true
                    );
                }
            })
            .catch(error => {
                showReviewNotification("Serverdə xəta baş verdi.", true);
            });
        });
    }
});

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

function showReviewNotification(message, isError = false, mehsulData = null) {
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


