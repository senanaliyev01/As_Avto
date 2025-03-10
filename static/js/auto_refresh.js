document.addEventListener('DOMContentLoaded', function() {
    function updateCountdowns() {
        document.querySelectorAll('.countdown').forEach(function(element) {
            const createdAt = new Date(element.dataset.created);
            const now = new Date();
            const expirationTime = new Date(createdAt.getTime() + 3 * 60 * 1000); // 3 dəqiqə
            
            if (now <= expirationTime) {
                const remaining = Math.floor((expirationTime - now) / 1000);
                const minutes = Math.floor(remaining / 60);
                const seconds = remaining % 60;
                element.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                // Son 30 saniyədə qırmızı rəng
                if (remaining <= 30) {
                    element.style.color = 'red';
                    element.style.fontWeight = 'bold';
                }
            } else {
                element.textContent = 'Vaxt bitib';
                element.style.color = 'red';
                
                // Status badge-i yenilə
                const row = element.closest('tr');
                if (row) {
                    const statusBadge = row.querySelector('.status-badge');
                    if (statusBadge) {
                        statusBadge.style.color = 'red';
                        statusBadge.textContent = 'BİTİB';
                    }
                }
            }
        });
    }

    // Hər saniyədə yenilə
    setInterval(updateCountdowns, 1000);

    // Səhifəni hər 30 saniyədə yenilə
    setInterval(function() {
        window.location.reload();
    }, 30000);
}); 