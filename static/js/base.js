document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    initializeSearch();
    
    // Cart functionality
    initializeCart();
    
    // Modal functionality
    initializeModal();
    
    // Initialize Swiper
    initializeSwiper();
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
    const checkoutForm = document.getElementById('checkout-form');

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

        // Update form confirmation
        document.querySelectorAll('.update-form').forEach(form => {
            form.addEventListener('submit', function(e) {
                if (form.closest('tr').querySelector('.item-checkbox').checked) {
                    if (!confirm('Bu məhsul seçilmiş vəziyyətdədir. Yeniləmək istədiyinizə əminsiniz?')) {
                        e.preventDefault();
                    }
                }
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

        // Form submission handler
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.action;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message message-success';
                    messageDiv.innerHTML = `<i class="fas fa-check-circle"></i>${data.message}`;
                    
                    const messagesContainer = document.querySelector('.messages');
                    if (messagesContainer) {
                        messagesContainer.appendChild(messageDiv);
                        
                        // Remove message after 3 seconds
                        setTimeout(() => {
                            messageDiv.remove();
                        }, 3000);
                    }
                    
                    // Update cart count if exists
                    const cartCount = document.querySelector('.cart-count');
                    if (cartCount && data.cart_count) {
                        cartCount.textContent = data.cart_count;
                    }
                    
                    // Close modal
                    modal.style.display = 'none';
                } else {
                    // Show error message
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message message-error';
                    messageDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i>${data.message}`;
                    
                    const messagesContainer = document.querySelector('.messages');
                    if (messagesContainer) {
                        messagesContainer.appendChild(messageDiv);
                        
                        // Remove message after 3 seconds
                        setTimeout(() => {
                            messageDiv.remove();
                        }, 3000);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message message-error';
                messageDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i>Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.';
                
                const messagesContainer = document.querySelector('.messages');
                if (messagesContainer) {
                    messagesContainer.appendChild(messageDiv);
                    
                    // Remove message after 3 seconds
                    setTimeout(() => {
                        messageDiv.remove();
                    }, 3000);
                }
            });
        });
    }
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