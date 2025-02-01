document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form');
    const searchButton = document.getElementById('search-button');
    const buttonText = searchButton.querySelector('.button-text');
    const spinner = searchButton.querySelector('.spinner');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Formanın default davranışını dayandırıq

        // Buttonu loading vəziyyətinə keçiririk
        searchButton.classList.add('loading');
        buttonText.style.opacity = '0.5';
        spinner.style.display = 'inline-block';

        // 2 saniyə gözləyirik
        setTimeout(() => {
            // 2 saniyədən sonra formanı göndəririk
            searchButton.classList.remove('loading');
            buttonText.style.opacity = '1';
            spinner.style.display = 'none';
            
            // Formanı göndəririk
            searchForm.submit();
        }, 2000);
    });

    // Enter düyməsinə basıldıqda da eyni funksiyanı işə salırıq
    searchForm.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Formanın standart təqdim edilməsini dayandır
            searchButton.classList.add('loading');
            buttonText.style.opacity = '0.5';
            spinner.style.display = 'inline-block';

            // 2 saniyə gözləyirik
            setTimeout(() => {
                searchButton.classList.remove('loading');
                buttonText.style.opacity = '1';
                spinner.style.display = 'none';
                
                // Formanı göndəririk
                searchForm.submit();
            }, 2000);
        }
    });
});
