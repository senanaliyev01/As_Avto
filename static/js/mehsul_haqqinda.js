document.addEventListener('DOMContentLoaded', function() {
    const productImage = document.getElementById('productImage');
    const brandImage = document.getElementById('brandImage');
    
    // Hər şəkil üçün ayrı rotasiya dəyərləri
    const rotations = {
        product: { x: 0, y: 0 },
        brand: { x: 0, y: 0 }
    };
    
    let isDragging = false;
    let startX, startY;
    let currentElement = null;
    
    function handleStart(e, element, type) {
        isDragging = true;
        currentElement = { element, type };
        startX = e.pageX || e.touches[0].pageX;
        startY = e.pageY || e.touches[0].pageY;
        element.style.transition = 'none';
        e.preventDefault();
    }
    
    function handleMove(e) {
        if (!isDragging || !currentElement) return;
        
        e.preventDefault();
        const pageX = e.pageX || e.touches[0].pageX;
        const pageY = e.pageY || e.touches[0].pageY;
        
        const deltaX = pageX - startX;
        const deltaY = pageY - startY;
        
        // Fırlanma limitləri
        rotations[currentElement.type].y = Math.max(-180, Math.min(180, deltaX * 0.5));
        rotations[currentElement.type].x = Math.max(-30, Math.min(30, -deltaY * 0.5));
        
        currentElement.element.style.transform = `
            perspective(1000px)
            rotateY(${rotations[currentElement.type].y}deg)
            rotateX(${rotations[currentElement.type].x}deg)
        `;
    }
    
    function handleEnd() {
        if (!isDragging || !currentElement) return;
        
        isDragging = false;
        currentElement.element.style.transition = 'transform 0.5s ease';
        currentElement.element.style.transform = 'perspective(1000px) rotateY(0) rotateX(0)';
        
        // Rotasiya dəyərlərini sıfırla
        rotations[currentElement.type].x = 0;
        rotations[currentElement.type].y = 0;
        
        currentElement = null;
    }
    
    // Mouse events
    if (productImage) {
        productImage.addEventListener('mousedown', (e) => handleStart(e, productImage, 'product'));
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        document.addEventListener('mouseleave', handleEnd);
    }
    
    if (brandImage) {
        brandImage.addEventListener('mousedown', (e) => handleStart(e, brandImage, 'brand'));
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        document.addEventListener('mouseleave', handleEnd);
    }
    
    // Touch events
    if (productImage) {
        productImage.addEventListener('touchstart', (e) => handleStart(e, productImage, 'product'));
        productImage.addEventListener('touchmove', handleMove);
        productImage.addEventListener('touchend', handleEnd);
        productImage.addEventListener('touchcancel', handleEnd);
    }
    
    if (brandImage) {
        brandImage.addEventListener('touchstart', (e) => handleStart(e, brandImage, 'brand'));
        brandImage.addEventListener('touchmove', handleMove);
        brandImage.addEventListener('touchend', handleEnd);
        brandImage.addEventListener('touchcancel', handleEnd);
    }
    
    // Şəkillərin sürüklənməsini əngəlləmək
    document.addEventListener('dragstart', (e) => e.preventDefault());
});

document.addEventListener('DOMContentLoaded', function () {
    // Səbətə məhsul əlavə etmək
    const cartLinks = document.querySelectorAll('.cart-icon');

    cartLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Default yönləndirməni bloklayır

            const url = this.getAttribute('href'); // URL alır
            fetch(url) // Ajax vasitəsilə serverə sorğu göndərir
                .then(response => {
                    if (response.ok) {
                        showAnimatedMessage("Məhsul səbətə əlavə olundu!");
                        updateCartCount(); // Səbət sayını yeniləyir
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