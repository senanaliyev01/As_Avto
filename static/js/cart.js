function toggleAllItems(checkbox) {
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    itemCheckboxes.forEach(item => {
        item.checked = checkbox.checked;
    });
    updateTotalAmount();
    updateOrderButton();
}

function updateTotalAmount() {
    let total = 0;
    const checkedItems = document.querySelectorAll('.item-checkbox:checked');
    
    checkedItems.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const itemTotal = parseFloat(row.querySelector('.item-total').textContent);
        total += itemTotal;
    });
    
    document.getElementById('selected-total-amount').textContent = total.toFixed(2) + ' AZN';
    updateOrderButton();
}

function updateOrderButton() {
    const checkedItems = document.querySelectorAll('.item-checkbox:checked');
    const orderButton = document.getElementById('orderButton');
    orderButton.disabled = checkedItems.length === 0;
}

function handleOrderSubmit(event) {
    event.preventDefault();
    
    const checkedItems = document.querySelectorAll('.item-checkbox:checked');
    if (checkedItems.length === 0) {
        showAnimatedMessage('Zəhmət olmasa ən azı bir məhsul seçin', true);
        return false;
    }
    
    if (confirm('Seçilmiş məhsulları sifariş etmək istədiyinizə əminsiniz?')) {
        const selectedItemIds = Array.from(checkedItems).map(checkbox => 
            checkbox.getAttribute('data-item-id')
        );
        
        const form = document.getElementById('orderForm');
        const submitUrl = form.getAttribute('data-submit-url');
        
        fetch(submitUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                selected_items: selectedItemIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAnimatedMessage('Sifarişiniz uğurla qeydə alındı!', false);
                
                // Loading bar göstər
                const loadingBar = document.getElementById('loadingBar');
                const progressBar = loadingBar.querySelector('.loading-bar-fill');
                const percentageText = loadingBar.querySelector('.loading-bar-percentage');
                
                loadingBar.style.display = 'block';
                
                let progress = 0;
                const duration = 3000; // 3 saniyə
                const interval = 30;
                const increment = (100 * interval) / duration;
                
                const updateProgress = setInterval(() => {
                    progress += increment;
                    if (progress >= 100) {
                        progress = 100;
                        clearInterval(updateProgress);
                        
                        // Sifarişlər səhifəsinə yönləndir
                        window.location.href = '/sifaris_izle/';
                    }
                    
                    progressBar.style.width = `${progress}%`;
                    percentageText.textContent = `${Math.round(progress)}%`;
                }, interval);
            } else {
                showAnimatedMessage(data.message || 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.', true);
            }
        })
        .catch(error => {
            console.error('Xəta:', error);
            showAnimatedMessage('Server xətası baş verdi. Zəhmət olmasa yenidən cəhd edin.', true);
        });
    }
    return false;
}

// Initialize order button state
document.addEventListener('DOMContentLoaded', function() {
    updateOrderButton();
});

function recalculateCart() {
    const loadingBar = document.getElementById('loadingBar');
    const progressBar = loadingBar.querySelector('.loading-bar-fill');
    const percentageText = loadingBar.querySelector('.loading-bar-percentage');
    const recalculateBtn = document.getElementById('recalculateBtn');
    
    // Düyməni deaktiv et
    recalculateBtn.disabled = true;
    recalculateBtn.style.opacity = '0.7';
    
    // Loading bar-ı göstər
    loadingBar.style.display = 'block';
    
    let progress = 0;
    const duration = 3000; // 3 saniyə
    const interval = 30; // Hər 30ms-də yenilənir
    const increment = (100 * interval) / duration;
    
    const updateProgress = setInterval(() => {
        progress += increment;
        if (progress >= 100) {
            progress = 100;
            clearInterval(updateProgress);
            
            // 3 saniyə sonra səhifəni yenilə
            setTimeout(() => {
                window.location.reload();
            }, 100);
        }
        
        progressBar.style.width = `${progress}%`;
        percentageText.textContent = `${Math.round(progress)}%`;
    }, interval);
}