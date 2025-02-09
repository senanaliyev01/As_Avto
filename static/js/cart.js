document.addEventListener('DOMContentLoaded', function() {
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

    // Ümumi məbləği yeniləmə funksiyası
    function updateTotalAmount() {
        const rows = document.querySelectorAll('tbody tr');
        let total = 0;

        rows.forEach(row => {
            const priceText = row.querySelector('.price').textContent;
            const quantity = parseInt(row.querySelector('.quantity-input').value);
            
            // Qiyməti təmizlə və ədədə çevir (vergüllü ədədlər üçün)
            const price = parseFloat(priceText.replace(' AZN', '').replace(',', '.').trim());
            
            // Hər məhsulun cəmini hesabla (2 rəqəmə qədər yuvarlaqlaşdır)
            const itemTotal = parseFloat((price * quantity).toFixed(2));
            
            // Sətrin cəmini yenilə
            row.querySelector('.item-total').textContent = itemTotal.toFixed(2) + ' AZN';
            
            // Ümumi cəmə əlavə et
            total += itemTotal;
        });

        // Ümumi məbləği 2 rəqəmə qədər yuvarlaqlaşdır
        total = parseFloat(total.toFixed(2));
        
        // Ümumi məbləği yenilə
        const totalElement = document.getElementById('total-amount');
        if (totalElement) {
            totalElement.textContent = total.toFixed(2) + ' AZN';
            
            // Real vaxtda cəmi məbləği base.html-da güncəlləyin
            fetch('/get_cart_total/')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        totalElement.textContent = data.total.toFixed(2) + ' AZN';
                    }
                });

            // Animasiya
            totalElement.classList.remove('update-animation');
            void totalElement.offsetWidth; // Reflow
            totalElement.classList.add('update-animation');
        }

        return total;
    }

    // Bildiriş göstərmə funksiyası
    function showNotification(message, type = 'success') {
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                </div>
                <div class="notification-message">${message}</div>
            </div>
            <div class="notification-progress"></div>
        `;

        document.body.appendChild(notification);

        // CSS stilləri
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '-400px',
            backgroundColor: type === 'success' ? '#4CAF50' : '#f44336',
            color: '#fff',
            padding: '15px',
            borderRadius: '8px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
            zIndex: '1000',
            transition: 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            minWidth: '300px'
        });

        // Bildirişi göstər
        setTimeout(() => {
            notification.style.right = '20px';
        }, 100);

        // Progress bar animasiyası
        const progress = notification.querySelector('.notification-progress');
        progress.style.cssText = `
            width: 100%;
            height: 3px;
            background: rgba(255, 255, 255, 0.5);
            position: absolute;
            bottom: 0;
            left: 0;
            border-radius: 0 0 8px 8px;
            animation: progress 3s linear forwards;
        `;

        // 3 saniyədən sonra bildirişi gizlət
        setTimeout(() => {
            notification.style.right = '-400px';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    // Məhsul silmə funksiyası
    window.removeItem = function(itemId) {
        // Mövcud modalı təmizlə
        const existingModal = document.querySelector('.delete-confirmation-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Yeni modal yarat
        const modal = document.createElement('div');
        modal.className = 'delete-confirmation-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;

        // Modal məzmunu
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background: linear-gradient(145deg, #0a1929, #1a2942);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            position: relative;
            transform: scale(0.7);
            opacity: 0;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        `;

        modalContent.innerHTML = `
            <div class="modal-icon" style="
                width: 70px;
                height: 70px;
                background: #ff5252;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
            ">
                <i class="fas fa-trash-alt" style="font-size: 30px; color: white;"></i>
            </div>
            <h3 style="color: white; margin-bottom: 10px; font-size: 1.5rem;">
                Məhsulu silmək istədiyinizə əminsiniz?
            </h3>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 25px;">
                Bu əməliyyat geri qaytarıla bilməz.
            </p>
            <div class="modal-buttons" style="
                display: flex;
                gap: 15px;
                justify-content: center;
            ">
                <button class="cancel-btn" style="
                    padding: 12px 25px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    background: #e0e0e0;
                    color: #333;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: transform 0.2s ease;
                ">
                    <i class="fas fa-times"></i> Xeyr
                </button>
                <button class="confirm-btn" style="
                    padding: 12px 25px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    background: #ff5252;
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: transform 0.2s ease;
                ">
                    <i class="fas fa-check"></i> Bəli
                </button>
            </div>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Modal animasiyası
        setTimeout(() => {
            modalContent.style.transform = 'scale(1)';
            modalContent.style.opacity = '1';
        }, 10);

        // Hover effektləri
        const buttons = modalContent.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('mouseover', () => {
                button.style.transform = 'translateY(-2px)';
                button.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
            });
            button.addEventListener('mouseout', () => {
                button.style.transform = 'translateY(0)';
                button.style.boxShadow = 'none';
            });
        });

        // Modal xaricində klikləmə
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeDeleteModal(modal);
            }
        });

        // Ləğv et düyməsi
        modalContent.querySelector('.cancel-btn').addEventListener('click', () => {
            closeDeleteModal(modal);
        });

        // Təsdiq düyməsi
        modalContent.querySelector('.confirm-btn').addEventListener('click', () => {
            // Düyməni deaktiv et
            const confirmBtn = modalContent.querySelector('.confirm-btn');
            const cancelBtn = modalContent.querySelector('.cancel-btn');
            confirmBtn.disabled = true;
            cancelBtn.disabled = true;
            confirmBtn.style.opacity = '0.7';
            cancelBtn.style.opacity = '0.7';

            // Loading ikonu əlavə et
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Silinir...';

            fetch(`/sebet/sil/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    closeDeleteModal(modal);
                    
                    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
                    if (row) {
                        // Sətri animasiya ilə sil
                        row.style.transition = 'all 0.3s ease';
                        row.style.transform = 'translateX(100%)';
                        row.style.opacity = '0';
                
                        setTimeout(() => {
                            row.remove();
                            // Ümumi məbləği yenilə
                            const newTotal = updateTotalAmount();
                            updateCartCount();
                            
                            // Bildiriş göstər
                            showNotification('Məhsul səbətdən silindi', 'success');
                    
                            // Səbət boşdursa səhifəni yenilə
                            if (document.querySelectorAll('tbody tr').length === 0) {
                                location.reload();
                            }
                        }, 300);
                    }
                } else {
                    closeDeleteModal(modal);
                    showNotification(data.message || 'Xəta baş verdi', 'error');
                }
            })
            .catch(error => {
                console.error('Xəta:', error);
                closeDeleteModal(modal);
                showNotification('Xəta baş verdi', 'error');
            });
        });
    };

    // Modal bağlama funksiyası
    function closeDeleteModal(modal) {
        const modalContent = modal.querySelector('.modal-content');
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        setTimeout(() => {
            modal.remove();
        }, 300);
    }

    // Səbət sayını yeniləmə funksiyası
    function updateCartCount() {
        fetch('/get_cart_count/')
            .then(response => response.json())
            .then(data => {
                const cartCount = document.querySelector('.cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                    cartCount.style.animation = 'bounce 0.5s ease';
                }
            })
            .catch(error => console.error('Xəta:', error));
    }

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
        const value = input.value.replace(/[^0-9]/g, '');
        const itemId = input.dataset.itemId;
        
        if (value === '' || value === '0') {
            input.value = '1';
            updateQuantity(itemId, 'set', 1);
        } else {
            updateQuantity(itemId, 'set', parseInt(value));
        }
    }, 300);

    // Miqdar yeniləmə funksiyası
    window.updateQuantity = function(itemId, value) {
        const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
        const input = row.querySelector('.quantity-input');
        let newQuantity;

        // Düymə ilə artırma/azaltma və ya birbaşa dəyər daxil etmə
        if (typeof value === 'number') {
            newQuantity = parseInt(input.value) + value;
        } else {
            newQuantity = parseInt(value);
        }

        // Minimum 1 olmasını təmin et
        if (isNaN(newQuantity) || newQuantity < 1) {
            newQuantity = 1;
            input.value = 1;
        }

        fetch(`/update_quantity/${itemId}/${newQuantity}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Input dəyərini yenilə
                    input.value = data.new_quantity;
                    
                    // Sətir cəmini yenilə
                    const itemTotalElement = row.querySelector('.item-total');
                    itemTotalElement.textContent = data.item_total.toFixed(2) + ' AZN';
                    
                    // Ümumi cəmi yenilə
                    const totalElement = document.getElementById('total-amount');
                    if (totalElement) {
                        totalElement.textContent = data.total_amount.toFixed(2) + ' AZN';
                    }

                    // Animasiya
                    row.classList.add('highlight');
                    setTimeout(() => row.classList.remove('highlight'), 300);
                } else {
                    // Xəta baş verdikdə əvvəlki dəyərə qayıt
                    input.value = input.defaultValue;
                    showNotification(data.error || 'Xəta baş verdi', 'error');
                }
            })
            .catch(error => {
                console.error('Xəta:', error);
                input.value = input.defaultValue;
                showNotification('Xəta baş verdi', 'error');
            });
    };

    // Sifariş təsdiqləmə funksiyası
    window.submitOrder = function() {
        fetch('/sifaris/gonder/', {
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
                closeModal('confirmModal');
                
                // Uğurlu modal göstər
                const successModal = document.getElementById('successModal');
                successModal.classList.add('show');
                
                // 3 saniyə sonra yönləndir və browser tarixçəsini təmizlə
                setTimeout(() => {
                    // Yeni URL-ə yönləndir və browser tarixçəsini əvəz et
                    window.location.replace('/orders/');
                    
                    // Əlavə təhlükəsizlik üçün history-ni təmizlə
                    window.history.pushState(null, '', '/orders/');
                    window.onpopstate = function(event) {
                        window.history.pushState(null, '', '/orders/');
                    };
                }, 3000);
            } else {
                throw new Error(data.message || 'Sifariş göndərilmədi');
            }
        })
        .catch(error => {
            closeModal('confirmModal');
            showNotification(error.message || 'Xəta baş verdi', 'error');
        });
    };

    // Modal funksiyaları
    window.closeModal = function(modalId = 'confirmModal') {
        const modal = document.getElementById(modalId);
        const modalContent = modal.querySelector('.modal-content');
        
        // Bağlanma animasiyası
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        
        setTimeout(() => {
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
                modalContent.style.transform = 'scale(1)';
                modalContent.style.opacity = '1';
            }, 300);
        }, 200);
    };

    window.confirmOrder = function() {
        const modal = document.getElementById('confirmModal');
        const modalContent = modal.querySelector('.modal-content');
        
        // Modal və content-i sıfırla
        modal.style.opacity = '0';
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        
        // Modalı göstər
        modal.style.display = 'flex';
        
        // Açılma animasiyası
        setTimeout(() => {
            modal.style.opacity = '1';
            modalContent.style.transform = 'scale(1)';
            modalContent.style.opacity = '1';
        }, 10);

    // Modal xaricində klikləmə
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
            closeModal();
        }
        });
    };

    // Uğurlu sifariş modalını göstər
    function showSuccessModal() {
        const modal = document.getElementById('successModal');
        const modalContent = modal.querySelector('.modal-content');
        
        // Modal və content-i sıfırla
        modal.style.opacity = '0';
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        
        // Modalı göstər
        modal.style.display = 'flex';
        
        // Açılma animasiyası
        setTimeout(() => {
            modal.style.opacity = '1';
            modalContent.style.transform = 'scale(1)';
            modalContent.style.opacity = '1';
        }, 10);
        
        // Modal xaricində klikləmə
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeSuccessModal();
            }
        });
    }

    // Uğurlu sifariş modalını bağla
    function closeSuccessModal() {
        const modal = document.getElementById('successModal');
        const modalContent = modal.querySelector('.modal-content');
        
        // Bağlanma animasiyası
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        
        setTimeout(() => {
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
                modalContent.style.transform = 'scale(1)';
                modalContent.style.opacity = '1';
                // Səhifəni yenilə
                window.location.href = '/';
            }, 300);
        }, 200);
    }

    // CSS stilləri əlavə et
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        @keyframes progress {
            to {
                width: 0%;
            }
        }

        .notification {
            display: flex;
            flex-direction: column;
        }

        .notification-content {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .notification-icon {
            font-size: 24px;
        }

        .notification-message {
            font-size: 16px;
            font-weight: 500;
        }

        .delete-confirmation-modal .modal-content {
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            position: relative;
            transition: transform 0.3s ease, opacity 0.3s ease;
        }

        .delete-confirmation-modal .modal-icon {
            width: 70px;
            height: 70px;
            background: #ff5252;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }

        .delete-confirmation-modal .modal-icon i {
            font-size: 30px;
            color: #fff;
        }

        .delete-confirmation-modal h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.5rem;
        }

        .delete-confirmation-modal p {
            color: #666;
            margin-bottom: 25px;
        }

        .delete-confirmation-modal .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        .delete-confirmation-modal button {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.2s ease;
        }

        .delete-confirmation-modal button:hover {
            transform: translateY(-2px);
        }

        .delete-confirmation-modal .confirm-btn {
            background: #ff5252;
            color: #fff;
        }

        .delete-confirmation-modal .cancel-btn {
            background: #e0e0e0;
            color: #333;
        }

        #confirmModal .modal-content {
            transition: transform 0.3s ease, opacity 0.3s ease;
        }

        .modal.show .modal-content {
            animation: modalShow 0.3s ease forwards;
        }

        @keyframes modalShow {
            from {
                transform: scale(0.7);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }

        @keyframes updateAnimation {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.1);
                color: #64ffda;
            }
            100% {
                transform: scale(1);
            }
        }

        .update-animation {
            animation: updateAnimation 0.5s ease;
        }
    `;

    document.head.appendChild(style);
});