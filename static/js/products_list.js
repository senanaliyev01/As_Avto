  // Hazırki saatı göstərmək
        function updateCurrentTime() {
            const currentTimeElement = document.getElementById('current-time');
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            currentTimeElement.textContent = `${hours}:${minutes}:${seconds}`;
        }

        // Hazırki saatı hər saniyə yeniləmək
        setInterval(updateCurrentTime, 1000);
        updateCurrentTime();

  document.addEventListener('DOMContentLoaded', function () {
    const cartLinks = document.querySelectorAll('.cart-icon');

    cartLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Default yönləndirməni bloklayır

            const url = this.getAttribute('href'); // URL alır
            fetch(url) // Ajax vasitəsilə serverə sorğu göndərir
                .then(response => {
                    if (response.ok) {
                        showAnimatedMessage("Məhsul səbətə əlavə olundu!");
                    } else {
                        showAnimatedMessage("Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.", true);
                    }
                })
                .catch(error => {
                    console.error("Xəta:", error);
                    showAnimatedMessage("Serverdə xəta baş verdi.", true);
                });
        });
    });

    function showAnimatedMessage(message, isError = false) {
        // Mesaj div-i yaradılır
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
});


  document.addEventListener('DOMContentLoaded', function () {
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
