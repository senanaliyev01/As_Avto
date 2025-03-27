document.addEventListener('DOMContentLoaded', function() {
    // Filter elementlərini əldə edir
    const categoryFilter = document.getElementById('category-filter');
    const brandFilter = document.getElementById('brand-filter');
    const modelFilter = document.getElementById('model-filter');
    const stockFilter = document.getElementById('stock-filter');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');
    const noResultsElement = document.getElementById('no-results');
    const productContainer = document.getElementById('product-container');
    
    // Bütün məhsul kartlarını seçir
    const productCards = document.querySelectorAll('.product-card');
    
    // Məhsul sayğacı əlavə edir
    addProductCounter();
    
    // URL parametrlərinə görə filterləri yükləyir
    loadFiltersFromURL();
    
    // İlkin sayğac yüklənir
    updateProductCount();
    
    // Filter dəyişiklik hadisəsi
    const filters = [categoryFilter, brandFilter, modelFilter, stockFilter];
    
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            applyFilters();
            updateURLParameters();
        });
    });
    
    // Filterləri təmizləmə düyməsinə klik hadisəsi
    clearFiltersBtn.addEventListener('click', function() {
        clearFilters();
        updateURLParameters();
    });
    
    // Xəta mesajının filter sıfırlama düyməsi
    resetFiltersBtn.addEventListener('click', function() {
        clearFilters();
        updateURLParameters();
    });
    
    // Filterləri təmizləyir
    function clearFilters() {
        categoryFilter.value = '';
        brandFilter.value = '';
        modelFilter.value = '';
        stockFilter.value = '';
        
        applyFilters();
    }
    
    // Filterləri tətbiq edir
    function applyFilters() {
        // Filterlər tətbiq olunarkən yüklənmə animasiyası
        const initialOpacity = window.getComputedStyle(productContainer).opacity;
        productContainer.style.opacity = "0.6";
        productContainer.style.transition = "opacity 0.3s ease";
        
        const categoryValue = categoryFilter.value.toLowerCase();
        const brandValue = brandFilter.value.toLowerCase();
        const modelValue = modelFilter.value.toLowerCase();
        const stockValue = stockFilter.value.toLowerCase();
        
        let visibleCount = 0;
        
        productCards.forEach(card => {
            const category = card.getAttribute('data-category').toLowerCase();
            const brand = card.getAttribute('data-brand').toLowerCase();
            const model = card.getAttribute('data-model').toLowerCase();
            const stock = card.getAttribute('data-stock').toLowerCase();
            
            // Filter şərtləri yoxlanır
            const matchesCategory = !categoryValue || category === categoryValue;
            const matchesBrand = !brandValue || brand === brandValue;
            const matchesModel = !modelValue || model === modelValue;
            const matchesStock = !stockValue || stock === stockValue;
            
            // Kart göstərilir və ya gizlədilir
            if (matchesCategory && matchesBrand && matchesModel && matchesStock) {
                card.style.display = 'block';
                card.classList.add('fade-in');
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.classList.remove('fade-in');
            }
        });
        
        // Nəticə olmadığı halda mesajı göstərir
        if (visibleCount === 0) {
            noResultsElement.style.display = 'block';
            noResultsElement.classList.add('fade-in');
        } else {
            noResultsElement.style.display = 'none';
            noResultsElement.classList.remove('fade-in');
        }
        
        // Məhsul sayını yeniləyir
        updateProductCount(visibleCount);
        
        // Animasiyanı tamamlayır
        setTimeout(() => {
            productContainer.style.opacity = initialOpacity;
        }, 300);
    }
    
    // URL parametrlərini yeniləyir
    function updateURLParameters() {
        const params = new URLSearchParams();
        
        if (categoryFilter.value) params.set('category', categoryFilter.value);
        if (brandFilter.value) params.set('brand', brandFilter.value);
        if (modelFilter.value) params.set('model', modelFilter.value);
        if (stockFilter.value) params.set('stock', stockFilter.value);
        
        // URL-i parametrlərlə yeniləyir
        const newURL = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
        window.history.replaceState({}, '', newURL);
    }
    
    // URL parametrlərindən filterləri yükləyir
    function loadFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        if (params.has('category')) categoryFilter.value = params.get('category');
        if (params.has('brand')) brandFilter.value = params.get('brand');
        if (params.has('model')) modelFilter.value = params.get('model');
        if (params.has('stock')) stockFilter.value = params.get('stock');
        
        // Parametrlər varsa filterləri tətbiq edir
        if (params.toString()) {
            applyFilters();
        }
    }
    
    // Məhsul sayğacı əlavə edir
    function addProductCounter() {
        const counter = document.createElement('div');
        counter.className = 'product-counter';
        counter.id = 'product-counter';
        counter.innerHTML = `Göstərilən məhsullar: <span class="counter-value">0</span> / <span class="counter-total">0</span>`;
        
        // Sayğacı filter konteynerinə əlavə edir
        const filterHeader = document.querySelector('.filter-header');
        if (filterHeader) {
            filterHeader.appendChild(counter);
        }
    }
    
    // Məhsul sayını yeniləyir
    function updateProductCount(count) {
        const totalCount = productCards.length;
        const visibleCount = count !== undefined ? count : totalCount;
        
        const counterValue = document.querySelector('.counter-value');
        const counterTotal = document.querySelector('.counter-total');
        
        if (counterValue && counterTotal) {
            counterValue.textContent = visibleCount;
            counterTotal.textContent = totalCount;
        }
    }

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

    // Səbət sayını yeniləmə funksiyası
    function updateCartCount() {
        fetch('/get_cart_count/')
            .then(response => response.json())
            .then(data => {
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                }
                
                // Səbət cəmini də yeniləyək
                if (data.total !== undefined) {
                    const cartTotalBadge = document.getElementById('cart-total-badge');
                    if (cartTotalBadge) {
                        cartTotalBadge.textContent = data.total + ' ₼';
                    }
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Bildiriş göstərmə funksiyası
    function showAnimatedMessage(message, isError = false, mehsulData = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'animated-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${!isError ? `
                    <div class="success-checkmark">
                        <div class="check-icon">
                            <i class="fas fa-check"></i>
                        </div>
                    </div>
                    <div class="message-text">
                        ${message}
                        ${mehsulData && mehsulData.adi ? `
                            <div class="product-info">
                                ${mehsulData.sekil ? 
                                    `<img src="${mehsulData.sekil}" alt="${mehsulData.adi}" class="product-image-image-tr">` 
                                    : ''
                                }
                                <span class="product-name">${mehsulData.adi}</span>
                                <span class="product-name">${mehsulData.oem}</span>
                            </div>
                        ` : ''}
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
            backgroundColor: isError ? '#dc3545' : '#003366',
            color: '#ffffff',
            padding: '15px 25px',
            borderRadius: '8px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.15)',
            zIndex: '2000',
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
                display: flex;
                align-items: center;
                justify-content: center;
                animation: pop 0.5s forwards;
            }
            .check-icon i {
                color: white;
                font-size: 16px;
            }
            @keyframes pop {
                0% { transform: scale(0) }
                50% { transform: scale(1.2) }
                100% { transform: scale(1) }
            }
            .product-info {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 10px 0;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 6px;
            }
            
            .product-image-image-tr {
                width: 80px;
                height: auto;
                object-fit: cover;
            }
            
            .product-name {
                font-size: 0.9em;
                font-weight: 500;
                color: #495057;
            }
            .quantity-error {
                position: absolute;
                bottom: -20px;
                left: 0;
                width: 100%;
                font-size: 0.75rem;
                color: #dc3545;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 2px 5px;
                border-radius: 4px;
                opacity: 0;
                transition: opacity 0.3s ease;
                text-align: center;
                z-index: 5;
            }
            
            .quantity-error.show {
                opacity: 1;
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

    // Seçilmiş miqdar ilə səbətə əlavə etmə funksiyası
    window.addToCartWithQuantity = function(productId) {
        const quantityInput = document.querySelector(`input[data-product-id="${productId}"]`);
        const quantity = parseInt(quantityInput.value);

        if (isNaN(quantity) || quantity <= 0) {
            showAnimatedMessage('Zəhmət olmasa düzgün miqdar daxil edin', true);
            return;
        }

        if (quantity > 999) {
            showAnimatedMessage('Maksimum 999 ədəd sifariş edə bilərsiniz', true);
            return;
        }

        const button = document.querySelector(`button[onclick="addToCartWithQuantity(${productId})"]`);
        const originalContent = button.innerHTML;

        // Loading effekti göstər
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.style.pointerEvents = 'none';
        button.style.opacity = '0.7';

        // 1 saniyə loading göstər
        setTimeout(() => {
            fetch(`/sebet/ekle/${productId}/?miqdar=${quantity}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                // Original ikonu bərpa et
                button.innerHTML = originalContent;
                button.style.pointerEvents = 'auto';
                button.style.opacity = '1';

                if (data.success) {
                    showAnimatedMessage(`${data.mehsul.adi} səbətə əlavə edildi (${quantity} ədəd)`, false, data.mehsul);
                    updateCartCount();
                } else {
                    showAnimatedMessage(data.error || 'Xəta baş verdi', true);
                }
            })
            .catch(error => {
                button.innerHTML = originalContent;
                button.style.pointerEvents = 'auto';
                button.style.opacity = '1';
                showAnimatedMessage('Xəta baş verdi', true);
                console.error('Error:', error);
            });
        }, 1000);
    }

    // Miqdar giriş validasiyası
    window.validateQuantity = function(input) {
        const value = parseInt(input.value);
        const errorDiv = input.parentElement.querySelector('.quantity-error');
        
        if (isNaN(value) || value < 1) {
            input.value = 1;
            errorDiv.textContent = 'Minimum miqdar 1 olmalıdır';
            errorDiv.classList.add('show');
            setTimeout(() => errorDiv.classList.remove('show'), 3000);
        } else if (value > 999) {
            input.value = 999;
            errorDiv.textContent = 'Maksimum miqdar 999 olmalıdır';
            errorDiv.classList.add('show');
            setTimeout(() => errorDiv.classList.remove('show'), 3000);
        }
    }
}); 