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
            event.preventDefault(); // Default yönləndirməni bloklayır

            // İkona loading effekti əlavə edir
            const icon = this.querySelector('i');
            icon.classList.add('fa-spinner', 'fa-spin');
            icon.classList.remove('fa-shopping-cart');

            setTimeout(() => {
                // 2 saniyə sonra loading tamamlanır
                icon.classList.remove('fa-spinner', 'fa-spin');
                icon.classList.add('fa-shopping-cart');

                // Mesaj göstərilir
                showAnimatedMessage("Məhsul səbətə əlavə olundu!");

                // Səbət sayını yeniləyir
                updateCartCount();
            }, 2000);
        });
    });

    // Mesaj animasiyası
    function showAnimatedMessage(message, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.innerText = message;
        messageDiv.style.position = 'fixed';
        messageDiv.style.top = '20px';
        messageDiv.style.right = '-300px'; // Sağdan başlayır
        messageDiv.style.backgroundColor = isError ? '#dc3545' : '#28a745'; // Xətalar üçün qırmızı, uğur üçün yaşıl
        messageDiv.style.color = 'white';
        messageDiv.style.padding = '10px 20px';
        messageDiv.style.borderRadius = '5px';
        messageDiv.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        messageDiv.style.zIndex = '1000';
        messageDiv.style.transition = 'right 0.5s ease'; // Animasiya

        document.body.appendChild(messageDiv);

        // Mesajın görünməsi
        setTimeout(() => {
            messageDiv.style.right = '20px'; // Sağdan sola hərəkət
        }, 10);

        // 3 saniyədən sonra mesajın yox olması
        setTimeout(() => {
            messageDiv.style.right = '-300px'; // Geri çəkilir
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 500); // Transition vaxtından sonra silinir
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
