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

document.addEventListener('DOMContentLoaded', function () {
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

            // 2 saniyə gözlə
            setTimeout(() => {
                fetch(url)
                    .then(response => {
                        if (response.ok) {
                            // Original ikonu bərpa et
                            this.innerHTML = originalContent;
                            this.style.pointerEvents = 'auto';
                            this.style.opacity = '1';

                            showAnimatedMessage("Məhsul səbətə əlavə olundu!");
                            updateCartCount();
                        } else {
                            this.innerHTML = originalContent;
                            this.style.pointerEvents = 'auto';
                            this.style.opacity = '1';
                            showAnimatedMessage("Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.", true);
                        }
                    })
                    .catch(error => {
                        console.error("Xəta:", error);
                        this.innerHTML = originalContent;
                        this.style.pointerEvents = 'auto';
                        this.style.opacity = '1';
                        showAnimatedMessage("Serverdə xəta baş verdi.", true);
                    });
            }, 2000); // 2 saniyə gözlə
        });
    });

    // Mesaj animasiyası
    function showAnimatedMessage(message, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'animated-message';
        
        // Professional görünüş üçün HTML strukturu
        messageDiv.innerHTML = `
            <div class="message-content">
                ${!isError ? `
                    <div class="success-checkmark">
                        <div class="check-icon">
                            <span class="icon-line line-tip"></span>
                            <span class="icon-line line-long"></span>
                        </div>
                    </div>
                    <div class="message-text">
                        ${message}
                        <div class="checkout-icon">
                            <i class="fas fa-shopping-cart"></i>
                            <span class="checkout-plus">+</span>
                            <span class="checkout-item"></span>
                        </div>
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
                transform: scale(0);
                animation: pop 0.5s forwards 0.5s;
            }
            .icon-line {
                height: 2px;
                position: absolute;
                background-color: #fff;
                border-radius: 2px;
            }
            .line-tip {
                top: 46%;
                left: 14%;
                width: 12px;
                transform: rotate(45deg);
                animation: icon-line-tip 0.75s forwards 0.5s;
            }
            .line-long {
                top: 38%;
                right: 8px;
                width: 16px;
                transform: rotate(-45deg);
                animation: icon-line-long 0.75s forwards 0.5s;
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
            @keyframes icon-line-tip {
                0% { width: 0; left: 1px; top: 19px; }
                54% { width: 0; left: 1px; top: 19px; }
                70% { width: 12px; left: -2px; top: 37px; }
                84% { width: 8px; left: 4px; top: 48px; }
                100% { width: 12px; left: 2px; top: 45%; }
            }
            @keyframes icon-line-long {
                0% { width: 0; right: 46px; top: 54px; }
                65% { width: 0; right: 46px; top: 54px; }
                84% { width: 16px; right: 0px; top: 35px; }
                100% { width: 16px; right: 8px; top: 38%; }
            }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                20%, 60% { transform: translateX(-5px); }
                40%, 80% { transform: translateX(5px); }
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

  // Səbətə əlavə olunan məhsul sayını yeniləyir
  function updateCartCount() {
    fetch('/get_cart_count/')  // Backend-dən səbət sayını alır
        .then(response => response.json())
        .then(data => {
            document.getElementById('cart-count').textContent = data.count;
        });
}

// Hər dəfə səhifə yükləndikdə səbət sayını yenilə
updateCartCount();

// Yalnızca AJAX ilə səbətə məhsul əlavə edildikdən sonra səbət sayını yeniləyəcək
const addToCartButtons = document.querySelectorAll('.cart-icon');
addToCartButtons.forEach(button => {
    button.addEventListener('click', function () {
        updateCartCount();
    });
});
});


document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form');
    const searchButton = document.getElementById('search-button');
    const buttonText = searchButton.querySelector('.button-text');
    const spinner = searchButton.querySelector('.spinner');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Formanın default davranışını dayandırıq

        // Buttonu loading vəziyyətinə keçiririk
        searchButton.classList.add('loading');
        buttonText.style.opacity = '0.5';
        spinner.style.display = 'inline-block';

        // 2 saniyə gözləyirik
        setTimeout(() => {
            // 2 saniyədən sonra formanı göndəririk
            searchButton.classList.remove('loading');
            buttonText.style.opacity = '1';
            spinner.style.display = 'none';
            
            // Formanı göndəririk
            this.submit();
        }, 2000);
    });
});

