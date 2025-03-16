function openModal(imgSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    
    // Modal pəncərəni göstər
    modal.style.display = "flex";
    
    // Şəkli yüklə və animasiya əlavə et
    modalImg.style.opacity = "0";
    modalImg.style.transform = "scale(0.5) rotate(-5deg)";
    modalImg.src = imgSrc;
    
    // Animasiyanı başlat
    requestAnimationFrame(() => {
        modal.classList.add('modal-open');
        modalImg.style.transition = "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)";
        modalImg.style.opacity = "1";
        modalImg.style.transform = "scale(1) rotate(0deg)";
    });

    // Escape düyməsi ilə bağlama
    document.addEventListener('keydown', closeOnEscape);
}

// Escape düyməsi ilə bağlama funksiyası
function closeOnEscape(e) {
    if (e.key === "Escape") {
        closeModal();
    }
}

// Modal pəncərəni bağlamaq üçün funksiya
function closeModal() {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    
    // Bağlanma animasiyasını başlat
    modal.classList.add('modal-closing');
    modalImg.style.opacity = "0";
    modalImg.style.transform = "scale(0.5) rotate(5deg)";
    
    // Animasiya bitdikdən sonra təmizlə
    setTimeout(() => {
        modal.style.display = "none";
        modal.classList.remove('modal-open', 'modal-closing');
        modalImg.style.transform = "";
        document.removeEventListener('keydown', closeOnEscape);
    }, 500);
}

// Bağlama düyməsinə klik
document.querySelector('.close-modal').onclick = closeModal;

// Modal xaricində kliklə bağlama
document.getElementById('imageModal').onclick = function(e) {
    if (e.target === this) {
        closeModal();
    }
}

// Şəklin yüklənməsini gözlə
document.getElementById('modalImage').onload = function() {
    this.style.opacity = "1";
    this.style.transform = "scale(1) rotate(0deg)";
}

// Axtarış sözlərini vurğulamaq üçün funksiya
function highlightSearchTerms() {
    // URL-dən axtarış parametrlərini əldə et
    const urlParams = new URLSearchParams(window.location.search);
    const searchText = urlParams.get('search_text');
    
    // Əgər axtarış sözü varsa
    if (searchText && searchText.trim() !== '') {
        // Axtarış sözlərini boşluqla ayır
        const searchTerms = searchText.trim().split(/\s+/).filter(term => term.length > 1);
        
        // Cədvəldəki bütün mətn hüceyrələrini seç
        const tableCells = document.querySelectorAll('.products-table tbody td:not(:first-child):not(:last-child):not(:nth-last-child(2))');
        
        // Hər bir hüceyrə üçün
        tableCells.forEach(cell => {
            const originalText = cell.textContent;
            
            // Hər bir axtarış sözü üçün
            searchTerms.forEach(term => {
                // Böyük-kiçik hərfə həssas olmayan regex
                const regex = new RegExp(`(${term})`, 'gi');
                
                // Əgər hüceyrədə axtarış sözü varsa
                if (regex.test(originalText)) {
                    // Axtarış sözünü vurğula
                    cell.innerHTML = originalText.replace(regex, '<span class="highlight-term">$1</span>');
                }
            });
        });
    }
}

// Səhifə yükləndikdə axtarış sözlərini vurğula
document.addEventListener('DOMContentLoaded', function() {
    highlightSearchTerms();
});