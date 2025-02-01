// Bu fayl artıq base.js-dəki funksionallıqdan istifadə edir
// Bütün axtarış forması funksionallığı base.js-ə köçürülüb

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form');
    const searchButton = document.getElementById('search-button');
    const buttonText = searchButton.querySelector('.button-text');
    const spinner = searchButton.querySelector('.spinner');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Əgər artıq loading vəziyyətindədirsə, təkrar işləməsin
        if (searchButton.classList.contains('loading')) {
            return;
        }

        // Buttonu loading vəziyyətinə keçiririk
        searchButton.classList.add('loading');
        buttonText.style.opacity = '0.5';
        spinner.style.display = 'inline-block';

        // 2 saniyə gözləyirik
        setTimeout(() => {
            // Formanı göndəririk
            searchForm.submit();
        }, 2000);
    });
});
