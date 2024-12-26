     // JavaScript kodu: Sifariş göndərmə təsdiqi
        function confirmOrder(event) {
            // Browser-in standart form göndərməsini dayandırırıq
            event.preventDefault();

            // Sual pəncərəsi
            const confirmation = confirm("Sifarişi təsdiq etmək istədiyinizə əminsiniz?");

            // Əgər "Bəli" düyməsinə basılıbsa, form göndərilsin
            if (confirmation) {
                // Formu göndəririk
                event.target.submit();
                alert("Sifarişiniz Uğurla Təsdiq Olundu !")
            }
        }

        document.addEventListener('DOMContentLoaded', function () {
    // Miqdar artırma düymələri üçün
    document.querySelectorAll('.increase').forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-id');
            updateQuantity(productId, 'increase');
        });
    });

    // Miqdar azaltma düymələri üçün
    document.querySelectorAll('.decrease').forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-id');
            updateQuantity(productId, 'decrease');
        });
    });

    // Miqdar yeniləmə funksiyası
    function updateQuantity(productId, action) {
        fetch(`/update_quantity/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // CSRF tokeni əlavə edin
            },
            body: JSON.stringify({ id: productId, action: action })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Miqdar yenilənməsi
                const quantityElement = document.querySelector(`button[data-id="${productId}"]`).parentElement.querySelector('.quantity');
                quantityElement.textContent = data.new_quantity;
            } else {
                alert('Miqdarı yeniləmək mümkün olmadı.');
            }
        });
    }

    // CSRF tokeni əldə etmək
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
