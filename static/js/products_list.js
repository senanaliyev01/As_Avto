document.addEventListener('DOMContentLoaded', function() {
    // Məhsullar axtarış forması
    const productsSearchForm = document.getElementById('products-search-form');
    const productsSearchButton = document.getElementById('products-search-button');
    const productsSearchInput = document.getElementById('products-search-input');
    
    if (productsSearchForm && productsSearchButton) {
        const buttonText = productsSearchButton.querySelector('.button-text');
        const spinner = productsSearchButton.querySelector('.spinner');

        productsSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Loading effektini göstər
            productsSearchButton.classList.add('loading');
            buttonText.style.opacity = '0.5';
            spinner.style.display = 'inline-block';

            // 2 saniyə gözlə
            setTimeout(() => {
                // Loading effektini gizlət
                productsSearchButton.classList.remove('loading');
                buttonText.style.opacity = '1';
                spinner.style.display = 'none';

                // Formanı göndər
                this.submit();
            }, 2000);
        });

        // Enter düyməsinə basıldıqda formanı göndər
        if (productsSearchInput) {
            productsSearchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    productsSearchForm.submit();
                }
            });
        }
    }
});
