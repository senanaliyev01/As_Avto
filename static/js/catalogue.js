/**
 * Catalouge.js - Kataloq səhifəsi üçün JavaScript funksiyaları
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tab System
    const initTabs = () => {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanes = document.querySelectorAll('.tab-pane');
        
        if (!tabButtons.length) return;
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons and panes
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanes.forEach(pane => pane.classList.remove('active'));
                
                // Add active class to clicked button and corresponding pane
                button.classList.add('active');
                const tabId = button.getAttribute('data-tab');
                if (document.getElementById(tabId)) {
                    document.getElementById(tabId).classList.add('active');
                }
            });
        });
    };
    
    // Filter Accordion
    const initAccordion = () => {
        const accordionButtons = document.querySelectorAll('.accordion-button');
        
        if (!accordionButtons.length) return;
        
        accordionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target') || this.nextElementSibling.id;
                const panel = document.getElementById(targetId) || this.nextElementSibling;
                
                if (panel.style.maxHeight) {
                    panel.style.maxHeight = null;
                    this.classList.remove('active');
                } else {
                    panel.style.maxHeight = panel.scrollHeight + 'px';
                    this.classList.add('active');
                }
            });
        });
    };
    
    // Show/Hide code toggle
    const initCodeToggles = () => {
        const toggleButtons = document.querySelectorAll('.toggle-codes');
        
        if (!toggleButtons.length) return;
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const codeContainer = document.getElementById(targetId);
                
                if (!codeContainer) return;
                
                if (codeContainer.style.display === 'block') {
                    codeContainer.style.display = 'none';
                    const codesCount = codeContainer.querySelectorAll('.code-item').length || 
                                      codeContainer.querySelectorAll('div').length;
                    this.innerHTML = `<i class="fas fa-plus-circle"></i> Əlavə OEM Kodlar (${codesCount})`;
                } else {
                    codeContainer.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-minus-circle"></i> Gizlət';
                }
            });
        });
    };
    
    // AJAX Form Submission
    const initAjaxForms = () => {
        const searchForms = document.querySelectorAll('#product-search-form, #application-search-form, #vin-search-form');
        const searchModal = document.getElementById('searchResultsModal');
        const loadingSpinner = document.getElementById('loading-spinner');
        const searchResults = document.getElementById('search-results');
        const noResults = document.getElementById('no-results');
        
        if (!searchForms.length || !searchModal) return;
        
        // Modal Close Button
        const closeBtn = document.querySelector('.close-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                searchModal.classList.remove('active');
            });
            
            // Close modal when clicking outside
            window.addEventListener('click', (e) => {
                if (e.target === searchModal) {
                    searchModal.classList.remove('active');
                }
            });
        }
        
        searchForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const url = this.getAttribute('action');
                const searchParams = new URLSearchParams(formData);
                
                // Show modal and loading spinner
                searchModal.classList.add('active');
                if (loadingSpinner) loadingSpinner.style.display = 'flex';
                if (searchResults) searchResults.style.display = 'none';
                if (noResults) noResults.style.display = 'none';
                
                // AJAX request
                fetch(`${url}?${searchParams.toString()}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (loadingSpinner) loadingSpinner.style.display = 'none';
                    
                    if (data.results && data.results.length > 0) {
                        if (searchResults) {
                            // Generate results HTML
                            let resultsHTML = '<div class="results-table"><table>';
                            resultsHTML += '<thead><tr><th>Şəkil</th><th>Məhsul</th><th>Brend/Model</th><th>Kodlar</th><th>Qiymət</th><th></th></tr></thead><tbody>';
                            
                            data.results.forEach(item => {
                                resultsHTML += '<tr>';
                                
                                // Image
                                resultsHTML += `<td class="result-image">
                                    ${item.sekil_url ? `<img src="${item.sekil_url}" alt="${item.adi}">` : '<div class="no-image"><i class="fas fa-image"></i></div>'}
                                </td>`;
                                
                                // Product name
                                resultsHTML += `<td class="result-name">${item.adi}</td>`;
                                
                                // Brand/Model
                                resultsHTML += `<td class="result-brand">
                                    <div><strong>Brend:</strong> ${item.brend}</div>
                                    <div><strong>Model:</strong> ${item.marka}</div>
                                </td>`;
                                
                                // Codes
                                let kodlarHTML = '';
                                if (item.oem) kodlarHTML += `<div><strong>OEM:</strong> ${item.oem}</div>`;
                                if (item.as_kodu) kodlarHTML += `<div><strong>AS:</strong> ${item.as_kodu}</div>`;
                                if (item.brend_kod) kodlarHTML += `<div><strong>BREND:</strong> ${item.brend_kod}</div>`;
                                
                                // Extra OEM codes
                                if (item.oem_kodlar && item.oem_kodlar.length > 0) {
                                    kodlarHTML += `<div class="extra-codes">
                                        <button class="toggle-codes" data-id="${item.id}">
                                            Əlavə kodlar (${item.oem_kodlar.length})
                                        </button>
                                        <div class="hidden-codes" id="codes-${item.id}">
                                            ${item.oem_kodlar.map(kod => `<div>${kod}</div>`).join('')}
                                        </div>
                                    </div>`;
                                }
                                
                                resultsHTML += `<td class="result-codes">${kodlarHTML}</td>`;
                                
                                // Price
                                resultsHTML += `<td class="result-price">${item.qiymet} AZN</td>`;
                                
                                // Actions
                                resultsHTML += `<td class="result-actions">
                                    <a href="${item.url}" class="action-button view-button">
                                        <i class="fas fa-eye"></i> Ətraflı
                                    </a>
                                </td>`;
                                
                                resultsHTML += '</tr>';
                            });
                            
                            resultsHTML += '</tbody></table></div>';
                            
                            // Update results container
                            searchResults.innerHTML = resultsHTML;
                            searchResults.style.display = 'block';
                            
                            // Initialize code toggles in the results
                            setTimeout(() => {
                                initCodeToggles();
                            }, 100);
                        }
                    } else {
                        if (noResults) noResults.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                    if (loadingSpinner) loadingSpinner.style.display = 'none';
                    if (noResults) {
                        noResults.style.display = 'block';
                        noResults.innerHTML = '<p><i class="fas fa-exclamation-circle"></i><br>Xəta baş verdi. Zəhmət olmasa, bir az sonra yenidən cəhd edin.</p>';
                    }
                });
            });
        });
    };
    
    // Add to Cart
    const initAddToCart = () => {
        const addToCartButtons = document.querySelectorAll('.add-to-cart');
        
        if (!addToCartButtons.length) return;
        
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const url = this.getAttribute('href');
                
                // AJAX request
                fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Success notification
                        showNotification('success', 'Məhsul səbətə əlavə edildi');
                        
                        // Update cart count if header contains cart badge
                        updateCartCount();
                    } else {
                        showNotification('error', data.error || 'Xəta baş verdi');
                    }
                })
                .catch(error => {
                    console.error('Add to cart error:', error);
                    showNotification('error', 'Xəta baş verdi. Zəhmət olmasa, yenidən cəhd edin.');
                });
            });
        });
    };
    
    // Show notification
    const showNotification = (type, message) => {
        const notification = document.createElement('div');
        notification.className = `add-cart-notification ${type}`;
        notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : 'times'}-circle"></i> ${message}`;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 3000);
    };
    
    // Update cart count
    const updateCartCount = () => {
        const cartCountElements = document.querySelectorAll('.cart-count-badge');
        
        if (!cartCountElements.length) return;
        
        fetch('/mehsullar/get_cart_count/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            cartCountElements.forEach(element => {
                element.textContent = data.count;
            });
        })
        .catch(error => console.error('Update cart count error:', error));
    };
    
    // Initialize all components
    initTabs();
    initAccordion();
    initCodeToggles();
    initAjaxForms();
    initAddToCart();
}); 