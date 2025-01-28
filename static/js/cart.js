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
            const itemTotal = parseFloat(row.querySelector('.item-total').textContent);
            total += itemTotal;
        });

        const totalElement = document.getElementById('total-amount');
        if (totalElement) {
            totalElement.textContent = total.toFixed(2) + ' AZN';
            
            // Animasiya
            totalElement.style.animation = 'fadeIn 0.3s ease';
        }
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
        const modal = document.createElement('div');
        modal.className = 'delete-confirmation-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-icon">
                    <i class="fas fa-trash-alt"></i>
                </div>
                <h3>Məhsulu silmək istədiyinizə əminsiniz?</h3>
                <p>Bu əməliyyat geri qaytarıla bilməz.</p>
                <div class="modal-buttons">
                    <button class="cancel-btn">
                        <i class="fas fa-times"></i> Xeyr
                    </button>
                    <button class="confirm-btn">
                        <i class="fas fa-check"></i> Bəli
                    </button>
                </div>
            </div>
        `;

        // Modal stilləri
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
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        const modalContent = modal.querySelector('.modal-content');
        modalContent.style.cssText = `
            background: linear-gradient(145deg, #0a1929, #1a2942);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            color: #fff;
            position: relative;
            transform: scale(0.7);
            transition: transform 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
        `;

        document.body.appendChild(modal);
        requestAnimationFrame(() => {
            modal.style.opacity = '1';
            modalContent.style.transform = 'scale(1)';
        });

        // Modalın xaricində klikləmə
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modalContent.style.transform = 'scale(0.7)';
                modal.style.opacity = '0';
                setTimeout(() => modal.remove(), 300);
            }
        });

        // Təsdiq və ləğv düymələri
        modal.querySelector('.cancel-btn').onclick = () => {
            modalContent.style.transform = 'scale(0.7)';
            modal.style.opacity = '0';
            setTimeout(() => modal.remove(), 300);
        };

        modal.querySelector('.confirm-btn').onclick = () => {
            modalContent.style.transform = 'scale(0.7)';
            modal.style.opacity = '0';
            
            fetch(`/sebet/sil/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
                    row.style.animation = 'slideOut 0.3s ease forwards';
                    
                    setTimeout(() => {
                        row.remove();
                        updateTotalAmount();
                        updateCartCount();
                        showNotification('Məhsul səbətdən silindi', 'success');
                        
                        if (document.querySelectorAll('tbody tr').length === 0) {
                            location.reload();
                        }
                    }, 300);
                } else {
                    showNotification(data.message || 'Xəta baş verdi', 'error');
                }
            })
            .catch(error => {
                console.error('Xəta:', error);
                showNotification('Xəta baş verdi', 'error');
            });

            setTimeout(() => modal.remove(), 300);
        };

        // Modal düymələrinin stilləri
        const buttons = modal.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.cssText = `
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: transform 0.2s ease;
            `;
        });

        const confirmBtn = modal.querySelector('.confirm-btn');
        confirmBtn.style.cssText += `
            background: #ff5252;
            color: #fff;
        `;

        const cancelBtn = modal.querySelector('.cancel-btn');
        cancelBtn.style.cssText += `
            background: #e0e0e0;
            color: #333;
        `;

        // Modal ikonunun stili
        const modalIcon = modal.querySelector('.modal-icon');
        modalIcon.style.cssText = `
            width: 70px;
            height: 70px;
            background: #ff5252;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        `;

        modalIcon.querySelector('i').style.cssText = `
            font-size: 30px;
            color: #fff;
        `;

        // Modal mətnlərinin stilləri
        const modalTitle = modal.querySelector('h3');
        modalTitle.style.cssText = `
            color: #fff;
            margin-bottom: 10px;
            font-size: 1.5rem;
        `;

        const modalText = modal.querySelector('p');
        modalText.style.cssText = `
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 25px;
        `;

        const modalButtons = modal.querySelector('.modal-buttons');
        modalButtons.style.cssText = `
            display: flex;
            gap: 15px;
            justify-content: center;
        `;
    };

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
        
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        
        setTimeout(() => {
            modal.classList.remove('show');
            modalContent.style.transform = '';
            modalContent.style.opacity = '';
        }, 300);
    };

    window.confirmOrder = function() {
        const modal = document.getElementById('confirmModal');
        modal.classList.add('show');
        
        const modalContent = modal.querySelector('.modal-content');
        modalContent.style.transform = 'scale(0.7)';
        modalContent.style.opacity = '0';
        
        requestAnimationFrame(() => {
            modalContent.style.transform = 'scale(1)';
            modalContent.style.opacity = '1';
        });
    };

    // Modal xaricində klikləmə
    window.onclick = function(event) {
        const modal = document.getElementById('confirmModal');
        if (event.target === modal) {
            closeModal();
        }
    };

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
    `;

    document.head.appendChild(style);
});