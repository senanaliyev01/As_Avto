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

    // Initialize Image Modal
    initializeImageModal();

    // Popup Modal
    initializePopupModal();

    // Add cart sidebar initialization
    initializeCartSidebar();

    // Initialize products page functionality
    initializeProductsPage();

    // Initialize Details Modal
    initializeDetailsModal();

    // Initialize User Details Modal
    initializeUserDetailsModal();

    // Initialize Logo Slider
    initializeLogoSlider();

    // Initialize Header Messages
    initializeHeaderMessages();

    // Initialize Admin Sidebar Toggle
    initializeAdminSidebar();

    setupCustomDropdown('category-dropdown', 'category');
    setupCustomDropdown('brand-dropdown', 'brand');
    setupCustomDropdown('model-dropdown', 'model');
    setupCustomDropdown('seller-dropdown', 'seller');

    // Buyer Stats Modal logic for my_sales.html
    initializeBuyerStatsModal();

    // Profile Modal logic
    initializeProfileModal();

    // Real-time sales notification
    let lastSalesCount = parseInt(localStorage.getItem('lastSalesCount') || '0', 10);
    let salesSound = null;

    function playSalesSound() {
        const audio = new Audio('/static/sounds/new_order.mp3');
        audio.currentTime = 0;
        audio.play();
    }

    function updateSalesBadge(count) {
        const badge = document.getElementById('salesBadge');
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.textContent = '0';
            badge.style.display = 'none';
        }
    }

    function pollSalesCount() {
        fetch('/api/unread-sales-count/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                if (typeof data.count === 'number') {
                    updateSalesBadge(data.count);
                    if (data.count > lastSalesCount) {
                        playSalesSound();
                    }
                    lastSalesCount = data.count;
                    localStorage.setItem('lastSalesCount', lastSalesCount);
                }
            })
            .catch(() => {});
    }

    setInterval(pollSalesCount, 10000); // 10 saniyədən bir yoxla
    pollSalesCount(); // İlk yükləmədə də yoxla

    // Linkə kliklədikdə sayğacı sıfırla
    const salesLink = document.querySelector('.user-dropdown .mr-sls');
    if (salesLink) {
        salesLink.addEventListener('click', function() {
            fetch('/api/unread-sales-count/', { method: 'POST', credentials: 'same-origin' })
                .then(() => {
                    updateSalesBadge(0);
                    lastSalesCount = 0;
                    localStorage.setItem('lastSalesCount', '0');
                });
        });
    }

    // --- Buyer live dropdown for my_sales.html ---
    const buyerSearch = document.getElementById('buyerLiveSearch');
    const buyerDropdown = document.getElementById('buyerLiveDropdown');
    if (buyerSearch && buyerDropdown) {
        // Açmaq üçün inputa klik
        buyerSearch.addEventListener('focus', function() {
            buyerDropdown.style.display = 'block';
            filterBuyerDropdown(this.value);
        });
        // Yazdıqca filtrlə və aç
        buyerSearch.addEventListener('input', function() {
            buyerDropdown.style.display = 'block';
            filterBuyerDropdown(this.value);
            filterOrdersByBuyerInput(this.value);
        });
        // Seçimə klik
        buyerDropdown.addEventListener('click', function(e) {
            if (e.target.classList.contains('buyer-live-option')) {
                buyerSearch.value = e.target.textContent;
                buyerDropdown.style.display = 'none';
                filterOrdersByBuyerInput(e.target.textContent);
            }
        });
        // Çöldə kliklədikdə bağla
        document.addEventListener('click', function(e) {
            if (!buyerDropdown.contains(e.target) && e.target !== buyerSearch) {
                buyerDropdown.style.display = 'none';
            }
        });
        function filterBuyerDropdown(query) {
            const val = query.toLowerCase();
            buyerDropdown.querySelectorAll('.buyer-live-option').forEach(opt => {
                opt.style.display = opt.dataset.username.includes(val) ? '' : 'none';
            });
        }
        function filterOrdersByBuyerInput(query) {
            const val = query.toLowerCase();
            const rows = document.querySelectorAll('table.table tbody tr');
            rows.forEach(row => {
                const buyerCell = row.querySelector('td:nth-child(2) a');
                if (!buyerCell) return;
                const username = buyerCell.textContent.toLowerCase();
                row.style.display = username.includes(val) ? '' : 'none';
            });
        }
    }
});

// Admin Sidebar Toggle Functionality
function initializeAdminSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminSidebar = document.getElementById('adminSidebar');
    const adminMain = document.getElementById('adminMain');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (!sidebarToggle || !adminSidebar || !adminMain) return;
    
    // Local storage-dan sidebar vəziyyətini al
    const isSidebarCollapsed = localStorage.getItem('adminSidebarCollapsed') === 'true';
    const isMobile = window.innerWidth <= 900;
    
    // İlk yükləmədə vəziyyəti tətbiq et
    if (isSidebarCollapsed && !isMobile) {
        adminSidebar.classList.add('collapsed');
        adminMain.style.marginLeft = '60px';
    }
    
    // Toggle button event listener
    sidebarToggle.addEventListener('click', function() {
        if (isMobile) {
            // Mobil üçün overlay ilə aç/bağla
            adminSidebar.classList.toggle('mobile-open');
            sidebarOverlay.classList.toggle('active');
            document.body.style.overflow = adminSidebar.classList.contains('mobile-open') ? 'hidden' : '';
        } else {
            // Desktop üçün collapse/expand
            adminSidebar.classList.toggle('collapsed');
            const isCollapsed = adminSidebar.classList.contains('collapsed');
            
            if (isCollapsed) {
                adminMain.style.marginLeft = '60px';
            } else {
                adminMain.style.marginLeft = '0';
            }
            
            // Local storage-a saxla
            localStorage.setItem('adminSidebarCollapsed', isCollapsed);
        }
    });
    
    // Overlay click event (mobil üçün)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            adminSidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // ESC düyməsi ilə bağla (mobil üçün)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && adminSidebar.classList.contains('mobile-open')) {
            adminSidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    // Window resize event
    window.addEventListener('resize', function() {
        const newIsMobile = window.innerWidth <= 900;
        
        if (newIsMobile !== isMobile) {
            // Mobil vəziyyətdən desktop-a keçid
            if (!newIsMobile) {
                adminSidebar.classList.remove('mobile-open');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
                
                // Desktop vəziyyətini bərpa et
                const isCollapsed = localStorage.getItem('adminSidebarCollapsed') === 'true';
                if (isCollapsed) {
                    adminSidebar.classList.add('collapsed');
                    adminMain.style.marginLeft = '60px';
                } else {
                    adminSidebar.classList.remove('collapsed');
                    adminMain.style.marginLeft = '0';
                }
            } else {
                // Desktop-dan mobilə keçid
                adminSidebar.classList.remove('collapsed');
                adminMain.style.marginLeft = '0';
            }
        }
    });
}

function initializeSearch() {
    const searchInput = document.querySelector('.header-search-input');
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
                                                <b>Kod:</b> ${item.brend_kod}<br>
                                                ${item.oem ? `<b>OEM:</b> ${item.oem}<br>` : ''}
                                                ${item.olcu ? `<b>Ölçü:</b> ${item.olcu}<br>` : ''}
                                            </div>
                                            <div class="search-result-seller"><i class="fas fa-user"></i> ${item.satici || 'AS-AVTO'}</div>
                                        </div>
                                        <div class="search-result-price">${item.qiymet} ₼</div>
                                    `;
                                    div.addEventListener('click', () => {
                                        searchInput.value = item.brend_kod;
                                        searchResults.style.display = 'none';
                                        document.querySelector('.header-search-form').submit();
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
    const updateForms = document.querySelectorAll('.update-form');
    const checkoutForm = document.getElementById('checkout-form');

    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            // Sifarişi göndərmədən öncə təsdiq istə
            if (!confirm('Sifariş etmək istədiyinizə əminsiniz?')) {
                e.preventDefault(); // Əgər istifadəçi "Cancel" basarsa, formanın göndərilməsini dayandır
            }
        });
    }

    // Add event listener for update forms
    if (updateForms) {
        updateForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const productId = this.closest('tr').dataset.productId;
                
                fetch(`/cart/update/${productId}/`, {
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
                        // Update subtotal for this item
                        const row = this.closest('tr');
                        const subtotalCell = row.querySelector('.subtotal');
                        if (subtotalCell) {
                            subtotalCell.textContent = data.subtotal;
                        }
                        
                        // Update cart total
                        const cartTotal = document.getElementById('cart-total');
                        if (cartTotal && data.cart_total) {
                            cartTotal.textContent = data.cart_total;
                        }

                        // Update selected total if the item is checked
                        const checkbox = row.querySelector('.item-checkbox');
                        if (checkbox && checkbox.checked) {
                            updateSelectedTotal();
                        }
                        
                        // Show success message
                        showMessage('success', data.message);
                    } else {
                        showMessage('error', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
                });
            });
        });
    }

    if (selectAll && checkboxes.length > 0 && selectedTotal && checkoutButton) {
        function updateSelectedTotal() {
            let total = 0;
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    const row = checkbox.closest('tr');
                    const subtotalText = row.querySelector('.subtotal').textContent;
                    // Remove currency symbol and convert to number
                    const subtotal = parseFloat(subtotalText.replace(' ₼', '').replace(',', '.'));
                    if (!isNaN(subtotal)) {
                        total += subtotal;
                    }
                    row.classList.add('selected');
                } else {
                    checkbox.closest('tr').classList.remove('selected');
                }
            });
            
            // Format total with 2 decimal places and proper currency symbol
            selectedTotal.textContent = total.toFixed(2).replace('.', ',') + ' ₼';
            
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
    const modalContent = document.querySelector('.custom-quantity-modal-content');
    
    if (modal && closeBtn && form && modalContent) {
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
                // Handle empty cart in both main page and sidebar
                const cartContainer = document.querySelector('.cart-container');
                const cartHeader = document.querySelector('.cart-header');
                const sidebarContent = document.querySelector('.cart-sidebar-content');
                
                // Create empty cart message
                const emptyCartHTML = `
                    <div class="empty-cart" style="margin: 20px;">
                        <i class="fas fa-shopping-cart"></i>
                        <p>Səbətiniz boşdur.</p>
                        <a href="/products/" class="btn btn-primary">Məhsullara bax</a>
                    </div>
                `;
                
                // Update sidebar content if we're in the sidebar
                if (sidebarContent) {
                    sidebarContent.innerHTML = emptyCartHTML;
                }
                
                // Update main page content if we're on the cart page
                if (cartContainer) {
                    cartContainer.style.display = 'none';
                }
                if (cartHeader) {
                    cartHeader.style.display = 'none';
                }
                
                const mainContent = document.querySelector('.main-content .container');
                if (mainContent && !sidebarContent) {
                    // Remove any existing empty cart message
                    const existingEmptyCart = mainContent.querySelector('.empty-cart');
                    if (existingEmptyCart) {
                        existingEmptyCart.remove();
                    }
                    
                    // Add new empty cart message to main page
                    const emptyCartDiv = document.createElement('div');
                    emptyCartDiv.className = 'empty-cart';
                    emptyCartDiv.style.marginTop = '2rem';
                    emptyCartDiv.innerHTML = emptyCartHTML;
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

function initializeImageModal() {
    const modal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.image-modal-close');
    
    if (modal && closeBtn) {
        closeBtn.onclick = closeImageModal;
        
        // Modal xaricində kliklədikdə bağla
        modal.onclick = function(e) {
            if (e.target === modal) {
                closeImageModal();
            }
        };
        
        // ESC düyməsi ilə bağla
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeImageModal();
            }
        });
    }
}

function openImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    if (modal && modalImg && imageSrc) {
        modalImg.src = imageSrc;
        modal.style.display = 'block';
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    }
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

function initializePopupModal() {
    const modal = document.getElementById('popupModal');
    if (!modal) return;

    const closeBtn = document.querySelector('.popup-close');
    const yeniliklerLink = document.getElementById('yeniliklerLink');
    let popupSwiper = null;
    
    // Initialize Swiper function
    function initPopupSwiper() {
        if (popupSwiper) {
            popupSwiper.destroy();
        }
        
        popupSwiper = new Swiper('.popup-swiper', {
            loop: true,
            autoplay: {
                delay: 3000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            }
        });
    }
    
    // Check if we should show the popup
    function shouldShowPopup() {
        const lastShown = localStorage.getItem('lastPopupShown');
        if (!lastShown) return true;
        
        const thirtyMinutesInMs = 30 * 60 * 1000;
        const timeSinceLastShown = Date.now() - parseInt(lastShown);
        
        return timeSinceLastShown >= thirtyMinutesInMs;
    }

    // Function to show popup
    function showPopup() {
        modal.style.display = 'block';
        localStorage.setItem('lastPopupShown', Date.now().toString());
        // Initialize Swiper when modal is shown
        setTimeout(() => {
            initPopupSwiper();
        }, 100);
    }
    
    // Show modal initially if enough time has passed
    if (shouldShowPopup()) {
        showPopup();
    }

    // Yenilikler linkine klik edəndə modalı göstər
    if (yeniliklerLink) {
        yeniliklerLink.addEventListener('click', function(e) {
            e.preventDefault();
            showPopup();
        });
    }

    // Close modal when clicking close button
    closeBtn.onclick = function() {
        modal.style.display = 'none';
        // Destroy Swiper instance when modal is closed
        if (popupSwiper) {
            popupSwiper.destroy();
            popupSwiper = null;
        }
    }

    // Prevent modal from closing when clicking inside modal content
    const popupContent = document.querySelector('.popup-content');
    if (popupContent) {
        popupContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
}

function initializeCartSidebar() {
    const cartToggle = document.getElementById('cartSidebarToggle');
    const cartSidebar = document.getElementById('cartSidebar');
    const closeSidebar = document.getElementById('closeSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (cartToggle && cartSidebar && closeSidebar && overlay) {
        // Load cart content when sidebar is opened
        function loadCartContent() {
            fetch('/cart/')
                .then(response => response.text())
                .then(html => {
                    // Create a temporary container
                    const temp = document.createElement('div');
                    temp.innerHTML = html;
                    
                    // Find the cart container in the response
                    const cartContent = temp.querySelector('.cart-container');
                    
                    // Update the sidebar content
                    const sidebarContent = document.querySelector('.cart-sidebar-content');
                    
                    if (cartContent) {
                        sidebarContent.innerHTML = cartContent.outerHTML;
                    } else {
                        // Create empty cart message for sidebar
                        sidebarContent.innerHTML = `
                            <div class="empty-cart" style="margin: 20px;">
                                <i class="fas fa-shopping-cart"></i>
                                <p>Səbətiniz boşdur.</p>
                                <a href="/products/" class="btn btn-primary">Məhsullara bax</a>
                            </div>
                        `;
                    }
                    
                    // Reinitialize cart functionality for the loaded content
                    initializeCart();
                })
                .catch(error => {
                    console.error('Error loading cart content:', error);
                });
        }

        // Open sidebar
        cartToggle.addEventListener('click', function(e) {
            e.preventDefault();
            cartSidebar.classList.add('active');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            loadCartContent();
        });

        // Close sidebar
        function closeSidebarHandler() {
            cartSidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }

        closeSidebar.addEventListener('click', closeSidebarHandler);
        overlay.addEventListener('click', closeSidebarHandler);

        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && cartSidebar.classList.contains('active')) {
                closeSidebarHandler();
            }
        });
    }
}

// Products Page Functions
function initializeProductsPage() {
    let offset = 5;
    let loading = false;
    const tbody = document.getElementById('products-tbody');
    const spinner = document.getElementById('loading-spinner');
    let hasMore = false; // Bu dəyər HTML-dən gələcək

    // hasMore dəyərini HTML-dən alırıq
    if (tbody) {
        const hasMoreElement = document.querySelector('[data-has-more]');
        if (hasMoreElement) {
            hasMore = hasMoreElement.dataset.hasMore === 'true';
        }
    }

    function loadMoreProducts() {
        if (loading || !hasMore) return;
        
        loading = true;
        if (spinner) {
            spinner.style.display = 'flex';
        }
        
        const params = new URLSearchParams(window.location.search);
        params.append('offset', offset);
        
        // Determine if we're on the new products page
        const isNewProductsPage = window.location.pathname.includes('new-products');
        const endpoint = isNewProductsPage ? '/load-more-new-products/' : '/load-more-products/';
        
        setTimeout(() => {
            fetch(`${endpoint}?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    if (tbody) {
                        data.products.forEach(product => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td><img src="${product.sekil_url || '/static/images/no_image.webp'}" alt="${product.adi}" class="product-image" onclick="openImageModal('${product.sekil_url}')"></td>
                                <td>${product.brend_kod}</td>
                                <td>${product.firma}</td>
                                <td>
                                    <span class="product-name-ellipsis">${product.adi}</span>
                                    ${product.yenidir ? '<span class="new-badge">Yeni</span>' : ''}
                                </td>
                                <td>
                                    ${product.sahib_id ? `<a href="#" class=\"seller-link\" onclick=\"openUserDetailsModal(${product.sahib_id}); return false;\"><i class=\"fas fa-user\"></i> ${product.sahib_username}</a>` : 'AS-AVTO'}
                                </td>
                                <td>${product.stok}</td>
                                <td>${product.qiymet} ₼</td>
                                <td>
                                    <button type="button" 
                                            class="cart-add-btn" 
                                            ${product.stok === 0 ? 'disabled' : ''}
                                            onclick="openQuantityModal(${product.id}, ${product.stok})">
                                        <i class="fas fa-shopping-cart"></i>
                                    </button>
                                </td>
                                <td>
                                    <button type="button" 
                                            class="details-btn" 
                                            onclick="openDetailsModal(${product.id})">
                                        <i class="fas fa-info-circle"></i>
                                    </button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                        
                        hasMore = data.has_more;
                        offset += 5;
                        
                        // Initialize image modal for new images
                        initializeImageModal();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    loading = false;
                    if (spinner) {
                        spinner.style.display = 'none';
                    }
                });
        }, 500); // 0.5 saniyə gözləmə
    }

    // Scroll event listener
    if (tbody) {
        window.addEventListener('scroll', () => {
            if ((window.innerHeight + window.scrollY) >= document.documentElement.scrollHeight - 200) {
                loadMoreProducts();
            }
        });
    }
}

// User Details Modal Functions
function openUserDetailsModal(userId) {
    const modal = document.getElementById('userDetailsModal');
    if (!modal) return;

    // Fetch user details
    fetch(`/user-details/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update modal content
                document.getElementById('userDetailsUsername').textContent = data.user.username;
                document.getElementById('userDetailsPhone').textContent = data.user.phone || '-';
                document.getElementById('userDetailsAddress').textContent = data.user.address || '-';
                // Profil şəkli
                var img = document.getElementById('userDetailsImage');
                if (img && data.user.sekil_url) {
                    img.src = data.user.sekil_url;
                } else if (img) {
                    img.src = '/static/images/no_image.jpg';
                }
                // Show modal with animation
                modal.style.display = 'block';
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
            } else {
                showMessage('error', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        });
}

function closeUserDetailsModal() {
    const modal = document.getElementById('userDetailsModal');
    if (!modal) return;

    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

function initializeUserDetailsModal() {
    const modal = document.getElementById('userDetailsModal');
    const closeBtn = document.querySelector('.user-details-modal-close');
    
    if (modal && closeBtn) {
        closeBtn.onclick = closeUserDetailsModal;
        
        // Close modal when clicking outside
        modal.onclick = function(e) {
            if (e.target === modal) {
                closeUserDetailsModal();
            }
        };
        
        // Close modal with ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeUserDetailsModal();
            }
        });
    }
}

// Details Modal Functions
function openDetailsModal(productId) {
    const modal = document.getElementById('detailsModal');
    if (!modal) return;

    // Fetch product details
    fetch(`/product-details/${productId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update modal content
                document.getElementById('detailsImage').src = data.product.sekil_url;
                document.getElementById('detailsName').textContent = data.product.adi;
                document.getElementById('detailsCategory').textContent = data.product.kateqoriya || '-';
                document.getElementById('detailsFirma').textContent = data.product.firma;
                document.getElementById('detailsAvtomobil').textContent = data.product.avtomobil;
                document.getElementById('detailsBrendKod').textContent = data.product.brend_kod;
                document.getElementById('detailsOlcu').textContent = data.product.olcu || '-';
                document.getElementById('detailsQiymet').textContent = data.product.qiymet + ' ₼';
                document.getElementById('detailsStok').textContent = data.product.stok + ' ədəd';
                document.getElementById('detailsMelumat').textContent = data.product.melumat || '-';

                // Seller info
                const detailsSeller = document.getElementById('detailsSeller');
                if (detailsSeller) {
                    if (data.product.sahib_id && data.product.sahib_username) {
                        detailsSeller.innerHTML = `<a href="#" class="seller-link" onclick="openUserDetailsModal(${data.product.sahib_id}); return false;"><i class="fas fa-user"></i> ${data.product.sahib_username}</a>`;
                    } else {
                        detailsSeller.textContent = 'AS-AVTO';
                    }
                }

                // Show modal with animation
                modal.style.display = 'block';
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
            } else {
                showMessage('error', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        });
}

function closeDetailsModal() {
    const modal = document.getElementById('detailsModal');
    if (!modal) return;

    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// Initialize Details Modal
function initializeDetailsModal() {
    const modal = document.getElementById('detailsModal');
    const closeBtn = document.querySelector('.details-modal-close');
    
    if (modal && closeBtn) {
        closeBtn.onclick = closeDetailsModal;
        
        // Close modal when clicking outside
        modal.onclick = function(e) {
            if (e.target === modal) {
                closeDetailsModal();
            }
        };
        
        // Close modal with ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeDetailsModal();
            }
        });
    }
}

// Initialize Logo Slider
function initializeLogoSlider() {
    const logoSwiper = new Swiper('.logo-swiper', {
        slidesPerView: 'auto',
        spaceBetween: 3,
        loop: true,
        autoplay: {
            delay: 2000,
            disableOnInteraction: false,
        },
        breakpoints: {
            320: {
                slidesPerView: 4,
                spaceBetween: 0
            },
            480: {
                slidesPerView: 6,
                spaceBetween: 0
            },
            768: {
                slidesPerView: 8,
                spaceBetween: 0
            },
            1024: {
                slidesPerView: 10,
                spaceBetween: 0
            }
        }
    });
}

function initializeHeaderMessages() {
    const messages = document.querySelectorAll('.message-slide');
    if (messages.length <= 1) return;

    let currentIndex = 0;
    const interval = 5000; // 5 saniyə
    const transitionDelay = 1000; // 1 saniyə keçid vaxtı

    function showMessage(index) {
        messages.forEach(msg => {
            msg.classList.remove('active');
            msg.style.display = 'none';
        });
        
        messages[index].style.display = 'block';
        // Force reflow
        void messages[index].offsetHeight;
        messages[index].classList.add('active');
    }

    function nextMessage() {
        currentIndex = (currentIndex + 1) % messages.length;
        showMessage(currentIndex);
    }

    // İlk mesajı göstər
    showMessage(0);

    // Hər 5 saniyədən bir növbəti mesaja keç
    setInterval(nextMessage, interval);
}

function setupCustomDropdown(dropdownId, selectId) {
    const dropdown = document.getElementById(dropdownId);
    const select = document.getElementById(selectId);
    if (!dropdown || !select) return;
    const input = dropdown.querySelector('.dropdown-search-input');
    const optionsContainer = dropdown.querySelector('.dropdown-options');
    const options = Array.from(optionsContainer.querySelectorAll('.dropdown-option'));

    // Show/hide dropdown
    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
        optionsContainer.style.display = 'block';
        input.focus();
    });
    // Filter options
    input.addEventListener('input', function() {
        const val = input.value.toLowerCase();
        options.forEach(opt => {
            if (opt.textContent.toLowerCase().includes(val)) {
                opt.style.display = '';
            } else {
                opt.style.display = 'none';
            }
        });
    });
    // Option click
    options.forEach(opt => {
        opt.addEventListener('click', function(e) {
            e.stopPropagation();
            // Set value in select
            select.value = opt.getAttribute('data-value');
            // Update input value
            input.value = opt.textContent;
            optionsContainer.style.display = 'none';
        });
    });
    // Click outside closes
    document.addEventListener('click', function() {
        optionsContainer.style.display = 'none';
    });
    // On page load, set input value to selected
    const selected = select.querySelector('option:checked');
    if (selected) {
        input.value = selected.textContent;
    }
}

// Buyer Stats Modal logic for my_sales.html
function initializeBuyerStatsModal() {
    const openBtn = document.getElementById('openStatsModal');
    const modal = document.getElementById('buyerStatsModal');
    const closeBtn = document.querySelector('.buyer-stats-modal-close');
    const searchInput = document.getElementById('buyerStatsSearch');
    const table = document.getElementById('buyerStatsTable');
    if (!openBtn || !modal || !closeBtn || !searchInput || !table) return;

    openBtn.addEventListener('click', function() {
        modal.style.display = 'block';
        setTimeout(() => modal.classList.add('show'), 10);
        searchInput.value = '';
        filterBuyerStatsTable('');
        searchInput.focus();
    });
    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeModal();
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') closeModal();
    });
    function closeModal() {
        modal.classList.remove('show');
        setTimeout(() => { modal.style.display = 'none'; }, 300);
    }
    searchInput.addEventListener('input', function() {
        filterBuyerStatsTable(this.value);
    });
    function filterBuyerStatsTable(query) {
        const rows = table.querySelectorAll('tbody tr');
        const val = query.toLowerCase();
        rows.forEach(row => {
            const username = row.querySelector('td').innerText.toLowerCase();
            row.style.display = username.includes(val) ? '' : 'none';
        });
    }
}

// Profile Modal logic
function initializeProfileModal() {
    const openBtn = document.getElementById('openProfileModal');
    const modal = document.getElementById('profileModal');
    const closeBtn = document.querySelector('.profile-modal-close');
    const form = document.getElementById('profileForm');
    const imageInput = document.getElementById('profileImageInput');
    const imagePreview = document.getElementById('profileImagePreview');
    if (!openBtn || !modal || !closeBtn || !form) return;

    // Open modal
    openBtn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.style.display = 'block';
        setTimeout(() => modal.classList.add('show'), 10);
    });
    // Close modal
    function closeModal() {
        modal.classList.remove('show');
        setTimeout(() => { modal.style.display = 'none'; }, 300);
    }
    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', function(e) {
        if (e.target === modal) closeModal();
    });
    window.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
    // Image preview
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    // AJAX submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch('/update-profile/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value || ''
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                // Update dropdown username, phone, address, image
                document.querySelectorAll('.user-name').forEach(el => {
                    el.innerHTML = '<i class="fas fa-user"></i> ' + data.username;
                });
                if (data.sekil_url) {
                    imagePreview.src = data.sekil_url;
                }
                // Optionally update phone/address elsewhere if needed
                closeModal();
                alert('Profil məlumatları yeniləndi!');
            } else {
                alert(data.message || 'Xəta baş verdi!');
            }
        })
        .catch(() => {
            alert('Xəta baş verdi!');
        });
    });
}

