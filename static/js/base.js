document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    initializeSearch();
    
    // Cart functionality
    initializeCart();
    
    // Modal functionality
    initializeModal();
    
    // Initialize Swiper
    initializeSwiper();

    // User dropdown functionality
    initializeUserDropdown();

    // Popup Modal
    const modal = document.getElementById('popupModal');
    if (!modal) return;

    const closeBtn = document.querySelector('.popup-close');
    const yeniliklerLink = document.getElementById('yeniliklerLink');
    
    // Check if we should show the popup
    function shouldShowPopup() {
        const lastShown = localStorage.getItem('lastPopupShown');
        if (!lastShown) return true;
        
        const thirtyMinutesInMs = 30 * 60 * 1000; // 30 minutes in milliseconds
        const timeSinceLastShown = Date.now() - parseInt(lastShown);
        
        return timeSinceLastShown >= thirtyMinutesInMs;
    }
    
    // Initialize Swiper for popup
    const popupSwiper = new Swiper('.popup-swiper', {
        loop: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });

    // Show modal only if enough time has passed
    if (shouldShowPopup()) {
        modal.style.display = 'block';
        localStorage.setItem('lastPopupShown', Date.now().toString());
    }

    // Yenilikler linkine klik edəndə modalı göstər
    if (yeniliklerLink) {
        yeniliklerLink.addEventListener('click', function(e) {
            e.preventDefault();
            modal.style.display = 'block';
            // Popup göstərilmə vaxtını yenilə
            localStorage.setItem('lastPopupShown', Date.now().toString());
        });
    }

    // Close modal when clicking close button
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }

    // Prevent modal from closing when clicking inside modal content
    const popupContent = document.querySelector('.popup-content');
    if (popupContent) {
        popupContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});

function initializeSearch() {
    const searchInput = document.getElementById('query');
    const searchResults = document.getElementById('search-results');
    let searchTimeout;

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length > 0) {
                searchTimeout = setTimeout(() => {
                    fetch(`/search-suggestions/?search=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            searchResults.innerHTML = '';
                            if (data.suggestions.length > 0) {
                                data.suggestions.forEach(item => {
                                    const div = document.createElement('div');
                                    div.className = 'search-result-item';
                                    div.innerHTML = `
                                        <img src="${item.sekil_url || '/static/images/no_image.jpg'}" alt="${item.adi}" class="search-result-image">
                                        <div class="search-result-info">
                                            <div class="search-result-title">${item.adi}</div>
                                            <div class="search-result-details">
                                                Brend Kodu: ${item.brend_kod}<br>
                                                OEM: ${item.oem}
                                            </div>
                                        </div>
                                        <div class="search-result-price">${item.qiymet} ₼</div>
                                    `;
                                    div.addEventListener('click', () => {
                                        searchInput.value = item.brend_kod;
                                        searchResults.style.display = 'none';
                                        document.querySelector('form.search-form').submit();
                                    });
                                    searchResults.appendChild(div);
                                });
                                searchResults.style.display = 'block';
                            } else {
                                searchResults.style.display = 'none';
                            }
                        });
                }, 300);
            } else {
                searchResults.style.display = 'none';
            }
        });

        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchResults.contains(e.target) && e.target !== searchInput) {
                searchResults.style.display = 'none';
            }
        });
    }
}

function initializeCart() {
    const selectAll = document.getElementById('select-all');
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const selectedTotal = document.getElementById('selected-total');
    const checkoutButton = document.getElementById('checkout-button');

    if (selectAll && checkboxes.length > 0 && selectedTotal && checkoutButton) {
        function updateSelectedTotal() {
            let total = 0;
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    const row = checkbox.closest('tr');
                    const subtotalText = row.querySelector('td:nth-last-child(2)').textContent;
                    const subtotal = Number(subtotalText.replace(' ₼', '').replace(',', '.'));
                    total += subtotal;
                    row.classList.add('selected');
                } else {
                    checkbox.closest('tr').classList.remove('selected');
                }
            });
            const formattedTotal = total.toFixed(2).replace('.', ',');
            selectedTotal.textContent = formattedTotal + ' ₼';
            
            const hasSelectedItems = Array.from(checkboxes).some(checkbox => checkbox.checked);
            checkoutButton.disabled = !hasSelectedItems;
        }

        selectAll.addEventListener('change', function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateSelectedTotal();
        });

        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                selectAll.checked = allChecked;
                updateSelectedTotal();
            });
        });
    }
}

function initializeModal() {
    const modal = document.getElementById('quantityModal');
    const closeBtn = document.querySelector('.close');
    const form = document.getElementById('addToCartForm');
    
    if (modal && closeBtn && form) {
        closeBtn.onclick = () => modal.style.display = 'none';
        
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        // Handle form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.action;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success message
                    showMessage('success', data.message);
                    // Update cart counter
                    if (data.cart_count !== undefined) {
                        updateCartCounter(data.cart_count);
                    }
                    // Close modal
                    modal.style.display = 'none';
                } else {
                    // Show error message
                    showMessage('error', data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
            });
        });
    }
}

// Function to remove item from cart
function removeFromCart(productId) {
    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Show success message
            showMessage('success', data.message);
            
            // Remove the row from the table
            const row = document.querySelector(`tr[data-product-id="${productId}"]`);
            if (row) {
                row.remove();
            }
            
            // Update cart counter
            if (data.cart_count !== undefined) {
                updateCartCounter(data.cart_count);
            }
            
            // Check if cart is empty
            const cartItems = document.querySelectorAll('.cart-item');
            if (cartItems.length === 0) {
                // Hide cart container and header
                const cartContainer = document.querySelector('.cart-container');
                const cartHeader = document.querySelector('.cart-header');
                
                if (cartContainer) {
                    cartContainer.style.display = 'none';
                }
                if (cartHeader) {
                    cartHeader.style.display = 'none';
                }
                
                // Find the main content container
                const mainContent = document.querySelector('.main-content .container');
                if (mainContent) {
                    // Create empty cart message
                    const emptyCartDiv = document.createElement('div');
                    emptyCartDiv.className = 'empty-cart';
                    emptyCartDiv.style.marginTop = '2rem';
                    emptyCartDiv.innerHTML = `
                        <p>Səbətiniz boşdur.</p>
                        <a href="/products/" class="btn btn-primary">Məhsullara bax</a>
                    `;
                    
                    // Remove any existing empty cart message
                    const existingEmptyCart = mainContent.querySelector('.empty-cart');
                    if (existingEmptyCart) {
                        existingEmptyCart.remove();
                    }
                    
                    // Add new empty cart message
                    mainContent.appendChild(emptyCartDiv);
                }
            }
        } else {
            showMessage('error', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
    });
}

// Function to get CSRF token
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

// Function to update cart total
function updateCartTotal() {
    const subtotalElements = document.querySelectorAll('.subtotal');
    let total = 0;
    
    subtotalElements.forEach(element => {
        const value = parseFloat(element.textContent.replace(' ₼', '').replace(',', '.'));
        if (!isNaN(value)) {
            total += value;
        }
    });
    
    const totalElement = document.getElementById('cart-total');
    if (totalElement) {
        totalElement.textContent = total.toFixed(2).replace('.', ',') + ' ₼';
    }
    
    // If cart is empty, show empty cart message
    const cartTable = document.querySelector('.table');
    const emptyCartMessage = document.querySelector('.empty-cart');
    
    if (subtotalElements.length === 0) {
        if (cartTable) cartTable.style.display = 'none';
        if (emptyCartMessage) emptyCartMessage.style.display = 'block';
    }
}

// Helper function to show messages
function showMessage(type, message) {
    const messagesContainer = document.createElement('div');
    messagesContainer.className = 'messages';
    messagesContainer.style.position = 'fixed';
    messagesContainer.style.top = '20px';
    messagesContainer.style.right = '-300px'; // Start off-screen
    messagesContainer.style.zIndex = '9999';
    messagesContainer.style.width = '300px';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    
    messageDiv.appendChild(icon);
    messageDiv.appendChild(document.createTextNode(' ' + message));
    messagesContainer.appendChild(messageDiv);
    
    document.body.appendChild(messagesContainer);
    
    // Animate in
    setTimeout(() => {
        messagesContainer.style.transition = 'right 0.5s ease';
        messagesContainer.style.right = '20px';
    }, 100);
    
    // Auto-hide message after 3 seconds
    setTimeout(() => {
        messagesContainer.style.right = '-300px';
        setTimeout(() => messagesContainer.remove(), 500);
    }, 3000);
}

// Modal functions
    window.openQuantityModal = function(productId, maxStock) {
        const modal = document.getElementById('quantityModal');
        const form = document.getElementById('addToCartForm');
        const quantityInput = document.getElementById('quantityInput');
        
        quantityInput.max = maxStock;
        form.action = `/cart/add/${productId}/`;
        modal.style.display = 'block';
    }

    window.closeQuantityModal = function() {
        const modal = document.getElementById('quantityModal');
        modal.style.display = 'none';
    }

function initializeSwiper() {
    if (document.querySelector('.new-products-swiper')) {
        new Swiper('.new-products-swiper', {
            slidesPerView: 4,
            spaceBetween: 20,
            loop: true,
            autoplay: {
                delay: 3000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            breakpoints: {
                320: {
                    slidesPerView: 1,
                    spaceBetween: 10
                },
                480: {
                    slidesPerView: 2,
                    spaceBetween: 15
                },
                768: {
                    slidesPerView: 3,
                    spaceBetween: 15
                },
                1024: {
                    slidesPerView: 4,
                    spaceBetween: 20
                }
            }
        });
    }
}

// Function to update cart counter
function updateCartCounter(count) {
    const counter = document.querySelector('.cart-counter');
    if (counter) {
        counter.textContent = count;
    }
}

// Function to get current cart count
function getCartCount() {
    const cart = JSON.parse(sessionStorage.getItem('cart') || '{}');
    return Object.keys(cart).length;
}

function initializeUserDropdown() {
    const userButton = document.querySelector('.user-button');
    const dropdownContent = document.querySelector('.user-dropdown-content');

    if (userButton && dropdownContent) {
        // Düyməyə klik hadisəsini əlavə edirik
        userButton.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownContent.classList.toggle('active');
            userButton.classList.toggle('active'); // Ox işarəsini çevirmək üçün
        });

        // Səhifənin istənilən yerinə klik edildikdə dropdown-u bağlayırıq
        document.addEventListener('click', function(e) {
            if (!dropdownContent.contains(e.target)) {
                dropdownContent.classList.remove('active');
                userButton.classList.remove('active'); // Ox işarəsini geri qaytarmaq üçün
            }
        });
    }
}