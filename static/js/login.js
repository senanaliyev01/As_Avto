window.addEventListener('DOMContentLoaded', () => {
    const messages = document.querySelectorAll('.messages .alert');

    // Mesaj varsa, göstər və 3 saniyə sonra sil
    if (messages.length > 0) {
        // Mesajları göstər
        document.querySelector('.messages').style.display = 'block';
        document.querySelector('.messages').style.opacity = 1;

        // 3 saniyə sonra mesajı sil
        setTimeout(() => {
            document.querySelector('.messages').style.opacity = 0;

            // 1 saniyə sonra tamamilə gizlən
            setTimeout(() => {
                document.querySelector('.messages').style.display = 'none';
            }, 1000);
        }, 3000);
    }
});
