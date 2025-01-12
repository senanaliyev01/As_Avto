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
        let totalEur = 0;
        let totalAzn = 0;

        rows.forEach(row => {
            const itemTotalEur = parseFloat(row.querySelector('.item-total div:first-child').textContent);
            const itemTotalAzn = parseFloat(row.querySelector('.item-total div:last-child').textContent);
            totalEur += itemTotalEur;
            totalAzn += itemTotalAzn;
        });

        const totalEurElement = document.getElementById('total-amount-eur');
        const totalAznElement = document.getElementById('total-amount-azn');
        
        if (totalEurElement && totalAznElement) {
            totalEurElement.textContent = totalEur.toFixed(2) + ' EUR';
            totalAznElement.textContent = totalAzn.toFixed(2) + ' AZN';
            
            // Animasiya
            totalEurElement.style.animation = 'fadeIn 0.3s ease';
            totalAznElement.style.animation = 'fadeIn 0.3s ease';
        }
    }

    // Bildiriş göstərmə funksiyası
    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // Məhsul silmə funksiyası
    window.removeItem = function(itemId) {
        if (!confirm('Bu məhsulu silmək istədiyinizə əminsiniz?')) return;

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
                
                // Silmədən əvvəl animasiya
                row.style.animation = 'slideOut 0.3s ease forwards';
                
                setTimeout(() => {
                    // Sətri sil
                    row.remove();
                    
                    // Ümumi cəmi yenilə
                    const totalElement = document.getElementById('total-amount');
                    if (totalElement) {
                        totalElement.textContent = data.cemi_mebleg.toFixed(2) + ' AZN';
                        totalElement.style.animation = 'fadeIn 0.3s ease';
                    }
                    
                    // Səbət boşdursa səhifəni yenilə
                    if (document.querySelectorAll('tbody tr').length === 0) {
                        location.reload();
                    }
                }, 300);

                // Səbət sayını yenilə
                updateCartCount();
                
                showNotification('Məhsul səbətdən silindi');
            } else {
                showNotification(data.message || 'Xəta baş verdi', 'error');
            }
        })
        .catch(error => {
            console.error('Xəta:', error);
            showNotification('Xəta baş verdi', 'error');
        });
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
        modal.classList.remove('show');
    };

    window.confirmOrder = function() {
        const modal = document.getElementById('confirmModal');
        modal.classList.add('show');
    };

    // Modal xaricində klikləmə
    window.onclick = function(event) {
        const modal = document.getElementById('confirmModal');
        if (event.target === modal) {
            closeModal();
        }
    };
});
