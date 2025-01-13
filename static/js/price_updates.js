function updatePrices() {
    fetch('/get_current_rates/')
        .then(response => response.json())
        .then(data => {
            document.querySelectorAll('.price-column').forEach(priceCol => {
                const newPrice = priceCol.querySelector('.new-price');
                if (newPrice) {
                    newPrice.classList.add('price-change-animation');
                    setTimeout(() => {
                        newPrice.classList.remove('price-change-animation');
                    }, 300);
                }
            });
        });
}

// Hər 10 dəqiqədən bir qiymətləri yenilə
setInterval(updatePrices, 600000); 