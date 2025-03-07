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
        alert('Zəhmət olmasa ən azı bir məhsul seçin');
        return false;
    }
    
    if (confirm('Seçilmiş məhsulları sifariş etmək istədiyinizə əminsiniz?')) {
        const selectedItemIds = Array.from(checkedItems).map(checkbox => 
            checkbox.getAttribute('data-item-id')
        );
        
        fetch('{% url "sifarisi_gonder" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                selected_items: selectedItemIds
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Sifarişiniz uğurla qeydə alındı. Sifarişlərim səhifəsinə yönləndirilirsiniz.');
                window.location.href = '{% url "sifaris_izle" %}';
            } else {
                alert('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
            }
        })
        .catch(error => {
            alert('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
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