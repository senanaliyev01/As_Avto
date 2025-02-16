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
            
            // Animasiya
            totalElement.classList.remove('update-animation');
            void totalElement.offsetWidth; // Reflow
            totalElement.classList.add('update-animation');
        }

        return total;
    }

    // Bildiriş göstərmə funksiyası
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 15px;
            border-radius: 4px;
            z-index: 1000;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
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

        if (typeof value === 'number') {
            newQuantity = parseInt(input.value) + value;
        } else {
            newQuantity = parseInt(value);
        }

        if (isNaN(newQuantity) || newQuantity < 1) {
            newQuantity = 1;
            input.value = 1;
        }

        // Düyməni deaktiv et və loading göstər
        const buttons = row.querySelectorAll('.quantity-btn');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.5';
        });
        input.disabled = true;

        fetch(`/update_quantity/${itemId}/${newQuantity}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    input.value = data.new_quantity;
                    const itemTotalElement = row.querySelector('.item-total');
                    itemTotalElement.textContent = data.item_total.toFixed(2) + ' AZN';
                    
                    const totalElement = document.getElementById('total-amount');
                    if (totalElement) {
                        totalElement.textContent = data.total_amount.toFixed(2) + ' AZN';
                    }

                    row.classList.add('highlight');
                    setTimeout(() => row.classList.remove('highlight'), 300);
                } else {
                    input.value = input.defaultValue;
                    showNotification(data.error || 'Xəta baş verdi', 'error');
                }
            })
            .catch(error => {
                console.error('Xəta:', error);
                input.value = input.defaultValue;
                showNotification('Xəta baş verdi', 'error');
            })
            .finally(() => {
                // Düymələri və inputu yenidən aktiv et
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
                input.disabled = false;
            });
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

        .highlight {
            animation: highlight 0.3s ease;
        }

        @keyframes highlight {
            0% {
                background-color: transparent;
            }
            50% {
                background-color: rgba(100, 255, 218, 0.2);
            }
            100% {
                background-color: transparent;
            }
        }
    `;

    document.head.appendChild(style);
});