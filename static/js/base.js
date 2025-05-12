// Axtarış funksionallığı
document.addEventListener('DOMContentLoaded', function() {
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

        // Axtarış nəticələri xaricində kliklədikdə bağlanır
        document.addEventListener('click', function(e) {
            if (!searchResults.contains(e.target) && e.target !== searchInput) {
                searchResults.style.display = 'none';
            }
        });
    }

    // Səbət funksionallığı
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

        // Yeniləmə formasının təsdiqlənməsi
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

    // Quantity Modal Functions
    window.openQuantityModal = function(productId, maxStock) {
        const modal = document.getElementById('quantityModal');
        const form = document.getElementById('addToCartForm');
        const quantityInput = document.getElementById('quantityInput');
        
        // Set max attribute
        quantityInput.max = maxStock;
        
        // Set form action
        form.action = `/cart/add/${productId}/`;
        
        // Show modal
        modal.style.display = 'block';
    }

    window.closeQuantityModal = function() {
        const modal = document.getElementById('quantityModal');
        modal.style.display = 'none';
    }

    // Close modal when clicking on X
    document.querySelector('.close').onclick = closeQuantityModal;

    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('quantityModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

document.addEventListener('DOMContentLoaded', function() {
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
});

// Cart Drawer Functionality
document.addEventListener('DOMContentLoaded', function() {
    const cartToggle = document.getElementById('cart-toggle');
    const cartDrawer = document.querySelector('.cart-drawer');
    const cartDrawerClose = document.querySelector('.cart-drawer-close');
    const body = document.body;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'cart-overlay';
    body.appendChild(overlay);

    function openCart() {
        cartDrawer.classList.add('open');
        overlay.classList.add('show');
        body.style.overflow = 'hidden';
        loadCartContent();
    }

    function closeCart() {
        cartDrawer.classList.remove('open');
        overlay.classList.remove('show');
        body.style.overflow = '';
    }

    function loadCartContent() {
        const cartBody = document.querySelector('.cart-drawer-body');
        fetch('/cart/')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const cartContent = doc.querySelector('.cart-container');
                if (cartContent) {
                    cartBody.innerHTML = cartContent.innerHTML;
                    initializeCartFunctionality();
                } else {
                    cartBody.innerHTML = '<div class="empty-cart"><p>Səbətiniz boşdur.</p><a href="/products/" class="btn btn-primary">Məhsullara bax</a></div>';
                }
            })
            .catch(error => {
                console.error('Error loading cart content:', error);
                cartBody.innerHTML = '<p>Səbət yüklənərkən xəta baş verdi.</p>';
            });
    }

    function initializeCartFunctionality() {
        // Update quantity form handling
        const updateForms = document.querySelectorAll('.cart-drawer-body .update-form');
        updateForms.forEach(form => {
            const quantityInput = form.querySelector('input[name="quantity"]');
            const originalValue = quantityInput.value;

            // Input change handler
            quantityInput.addEventListener('change', function(e) {
                if (this.value !== originalValue) {
                    const formData = new FormData(form);
                    const submitBtn = form.querySelector('button[type="submit"]');
                    
                    // Disable input and button while updating
                    this.disabled = true;
                    submitBtn.disabled = true;
                    
                    fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    }).then(response => {
                        if (response.ok) {
                            loadCartContent();
                        } else {
                            // If error, revert to original value
                            this.value = originalValue;
                            alert('Yeniləmə zamanı xəta baş verdi');
                        }
                    }).catch(error => {
                        console.error('Error:', error);
                        this.value = originalValue;
                        alert('Xəta baş verdi');
                    }).finally(() => {
                        // Re-enable input and button
                        this.disabled = false;
                        submitBtn.disabled = false;
                    });
                }
            });

            // Hide update button as we don't need it anymore
            const updateButton = form.querySelector('button[type="submit"]');
            if (updateButton) {
                updateButton.style.display = 'none';
            }
        });

        // Remove item form handling
        const removeForms = document.querySelectorAll('.cart-drawer-body .remove-form');
        removeForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const button = form.querySelector('button');
                button.disabled = true;
                
                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                }).then(response => {
                    if (response.ok) {
                        loadCartContent();
                    } else {
                        alert('Silmə zamanı xəta baş verdi');
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    alert('Xəta baş verdi');
                }).finally(() => {
                    button.disabled = false;
                });
            });
        });

        // Checkout form handling
        const checkoutForm = document.getElementById('checkout-form');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Çatdırılma üsulunu yoxla
                const deliveryMethod = document.querySelector('input[name="catdirilma_usulu"]:checked');
                if (!deliveryMethod) {
                    alert('Zəhmət olmasa çatdırılma üsulunu seçin');
                    return;
                }

                // Seçilmiş məhsulları yoxla
                const selectedItems = document.querySelectorAll('.item-checkbox:checked');
                if (selectedItems.length === 0) {
                    alert('Zəhmət olmasa ən azı bir məhsul seçin');
                    return;
                }

                const formData = new FormData(checkoutForm);
                fetch(checkoutForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                }).then(response => {
                    if (response.ok) {
                        window.location.href = '/orders/';
                    } else {
                        alert('Sifariş yaradılarkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    alert('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
                });
            });

            // Seçilmiş məhsulların ümumi məbləğini hesabla
            const checkboxes = document.querySelectorAll('.item-checkbox');
            const selectedTotal = document.getElementById('selected-total');
            const checkoutButton = document.getElementById('checkout-button');

            function updateSelectedTotal() {
                let total = 0;
                checkboxes.forEach(checkbox => {
                    if (checkbox.checked) {
                        const row = checkbox.closest('tr');
                        const subtotalText = row.querySelector('td:nth-last-child(2)').textContent;
                        const subtotal = parseFloat(subtotalText.replace(' ₼', '').replace(',', '.'));
                        total += subtotal;
                    }
                });
                selectedTotal.textContent = total.toFixed(2).replace('.', ',') + ' ₼';
                checkoutButton.disabled = total === 0;
            }

            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', updateSelectedTotal);
            });

            const selectAll = document.getElementById('select-all');
            if (selectAll) {
                selectAll.addEventListener('change', function() {
                    checkboxes.forEach(checkbox => {
                        checkbox.checked = this.checked;
                    });
                    updateSelectedTotal();
                });
            }
        }
    }

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

    if (cartToggle) {
        cartToggle.addEventListener('click', function(e) {
            e.preventDefault();
            openCart();
        });
    }

    if (cartDrawerClose) {
        cartDrawerClose.addEventListener('click', closeCart);
    }

    overlay.addEventListener('click', closeCart);
});