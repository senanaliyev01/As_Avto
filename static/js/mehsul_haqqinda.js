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

    // Yeni əlavə edilmiş funksionallıqlar
    
    // Tab sistemi
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Aktiv tab-ı təmizlə
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Yeni tab-ı aktiv et
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Şəkil böyütmə modal
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const captionText = document.getElementById('caption');
    const closeModal = document.querySelector('.close-modal');
    
    // Məhsul şəklini böyütmək
    if (productImage) {
        productImage.addEventListener('click', function() {
            modal.style.display = "block";
            modalImg.src = this.src;
            captionText.innerHTML = this.alt;
        });
    }
    
    // Brend şəklini böyütmək
    if (brandImage) {
        brandImage.addEventListener('click', function() {
            modal.style.display = "block";
            modalImg.src = this.src;
            captionText.innerHTML = this.alt;
        });
    }
    
    // Modalı bağlamaq
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modal.style.display = "none";
        });
    }
    
    // Modal xaricində klikləndikdə bağlamaq
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    });
    
    // Şəkil fırlatma düymələri
    const rotateLeft = document.getElementById('rotateLeft');
    const rotateRight = document.getElementById('rotateRight');
    let currentRotation = 0;
    
    if (rotateLeft && productImage) {
        rotateLeft.addEventListener('click', function() {
            currentRotation -= 90;
            productImage.style.transition = 'transform 0.5s ease';
            productImage.style.transform = `rotate(${currentRotation}deg)`;
        });
    }
    
    if (rotateRight && productImage) {
        rotateRight.addEventListener('click', function() {
            currentRotation += 90;
            productImage.style.transition = 'transform 0.5s ease';
            productImage.style.transform = `rotate(${currentRotation}deg)`;
        });
    }
    
    // İstək siyahısına əlavə etmə
    const wishlistButtons = document.querySelectorAll('.wishlist-button');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            
            // İkon dəyişdirmə
            const icon = this.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                showNotification('Məhsul istək siyahınıza əlavə edildi', 'success');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                showNotification('Məhsul istək siyahınızdan çıxarıldı', 'info');
            }
            
            // Burada AJAX ilə server-ə istək göndərmək olar
            // fetch('/istək-siyahısı/əlavə-et/' + productId, {...})
        });
    });
    
    // Sürətli səbətə əlavə etmə
    const quickAddButtons = document.querySelectorAll('.quick-add-to-cart');
    
    quickAddButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Animasiya
            this.classList.add('adding');
            setTimeout(() => {
                this.classList.remove('adding');
            }, 1000);
            
            // Burada AJAX ilə server-ə istək göndərmək olar
            fetch('/sebet/ekle/' + productId)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Məhsul səbətə əlavə edildi', 'success');
                    } else {
                        showNotification('Xəta baş verdi', 'error');
                    }
                })
                .catch(error => {
                    showNotification('Xəta baş verdi', 'error');
                });
        });
    });
    
    // Bildiriş göstərmə funksiyası
    function showNotification(message, type = 'info') {
        // Əvvəlki bildirişləri təmizlə
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => {
            notification.remove();
        });
        
        // Yeni bildiriş yarat
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Bildiriş ikonu
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle"></i>';
                break;
            case 'error':
                icon = '<i class="fas fa-times-circle"></i>';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-circle"></i>';
                break;
            default:
                icon = '<i class="fas fa-info-circle"></i>';
        }
        
        notification.innerHTML = `
            ${icon}
            <span>${message}</span>
            <button class="close-notification"><i class="fas fa-times"></i></button>
        `;
        
        document.body.appendChild(notification);
        
        // Bildirişi göstər
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Bildirişi bağlama düyməsi
        const closeButton = notification.querySelector('.close-notification');
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
    
    // Bildiriş stilləri
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        .notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 15px 20px;
            background: rgba(10, 25, 41, 0.9);
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .notification.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .notification.success {
            border-left: 4px solid #00897b;
        }
        
        .notification.error {
            border-left: 4px solid #e53935;
        }
        
        .notification.warning {
            border-left: 4px solid #ffb300;
        }
        
        .notification.info {
            border-left: 4px solid #1565c0;
        }
        
        .notification i {
            font-size: 1.2rem;
        }
        
        .notification.success i {
            color: #00897b;
        }
        
        .notification.error i {
            color: #e53935;
        }
        
        .notification.warning i {
            color: #ffb300;
        }
        
        .notification.info i {
            color: #1565c0;
        }
        
        .close-notification {
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            margin-left: 10px;
            padding: 0;
            font-size: 0.9rem;
            transition: color 0.2s ease;
        }
        
        .close-notification:hover {
            color: white;
        }
        
        @keyframes adding {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        
        .quick-add-to-cart.adding {
            animation: adding 0.5s ease;
        }
    `;
    
    document.head.appendChild(notificationStyles);
});