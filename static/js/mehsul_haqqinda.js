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
    
    // İstək siyahısı funksiyası
    const wishlistButton = document.querySelector('.wishlist-button');
    if (wishlistButton) {
        wishlistButton.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            
            // İkon dəyişdirmə
            const icon = this.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                
                // Animasiya əlavə et
                icon.classList.add('pulse-animation');
                setTimeout(() => {
                    icon.classList.remove('pulse-animation');
                }, 1000);
                
                showNotification('Məhsul istək siyahınıza əlavə edildi', 'success');
                
                // Burada istək siyahısına əlavə etmək üçün AJAX sorğusu göndərilə bilər
                // addToWishlist(productId);
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                showNotification('Məhsul istək siyahınızdan çıxarıldı', 'info');
                
                // Burada istək siyahısından çıxarmaq üçün AJAX sorğusu göndərilə bilər
                // removeFromWishlist(productId);
            }
        });
    }
    
    // Səbətə əlavə et düyməsi
    const cartButton = document.querySelector('.cart-icon');
    if (cartButton) {
        cartButton.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Animasiya əlavə et
            const icon = this.querySelector('i');
            icon.classList.add('bounce-animation');
            setTimeout(() => {
                icon.classList.remove('bounce-animation');
            }, 1000);
            
            // AJAX ilə səbətə əlavə et
            fetch(this.getAttribute('href'))
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Məhsul səbətə əlavə edildi', 'success');
                        // Səbət sayğacını yeniləmək üçün kod əlavə edilə bilər
                    } else {
                        showNotification(data.error || 'Xəta baş verdi', 'error');
                    }
                })
                .catch(error => {
                    showNotification('Xəta baş verdi', 'error');
                    console.error('Error:', error);
                });
        });
    }
    
    // Bildiriş göstərmə funksiyası
    function showNotification(message, type = 'info') {
        // Əvvəlki bildirişləri təmizlə
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => {
            notification.remove();
        });
        
        // Yeni bildiriş yaratma
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Bildiriş ikonu
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle"></i>';
                break;
            case 'error':
                icon = '<i class="fas fa-exclamation-circle"></i>';
                break;
            case 'info':
                icon = '<i class="fas fa-info-circle"></i>';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle"></i>';
                break;
        }
        
        notification.innerHTML = `
            <div class="notification-content">
                ${icon}
                <span>${message}</span>
            </div>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        document.body.appendChild(notification);
        
        // Bildirişi göstər
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Bildirişi bağla düyməsi
        const closeButton = notification.querySelector('.notification-close');
        closeButton.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Avtomatik bağlanma
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
    
    // CSS animasiyaları üçün stil əlavə et
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.3); }
            100% { transform: scale(1); }
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        .pulse-animation {
            animation: pulse 0.5s ease-in-out;
            color: #ff4081;
        }
        
        .bounce-animation {
            animation: bounce 0.8s ease;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            background: #fff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 300px;
            max-width: 450px;
            transform: translateX(120%);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .notification.success {
            background: linear-gradient(135deg, #00897b, #00695c);
            color: white;
        }
        
        .notification.error {
            background: linear-gradient(135deg, #e53935, #c62828);
            color: white;
        }
        
        .notification.info {
            background: linear-gradient(135deg, #1565c0, #0d47a1);
            color: white;
        }
        
        .notification.warning {
            background: linear-gradient(135deg, #ffd54f, #ffb300);
            color: black;
        }
        
        .notification-close {
            background: transparent;
            border: none;
            color: inherit;
            cursor: pointer;
            padding: 0;
            margin-left: 10px;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        
        .notification-close:hover {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);
});