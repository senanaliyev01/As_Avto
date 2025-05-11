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