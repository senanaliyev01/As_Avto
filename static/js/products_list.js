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
        // Axtarış sözlərini boşluqla ayır və yalnız hərf və rəqəmləri saxla
        const searchTerms = searchText.trim().split(/\s+/).filter(term => term.length > 1);
        
        // Cədvəldəki bütün mətn hüceyrələrini seç
        const tableCells = document.querySelectorAll('.products-table tbody td:not(:first-child):not(:last-child):not(:nth-last-child(2))');
        
        // Hər bir hüceyrə üçün
        tableCells.forEach(cell => {
            const originalText = cell.textContent;
            let cellHtml = originalText;
            
            // Hər bir axtarış sözü üçün
            searchTerms.forEach(term => {
                // Xüsusi simvolları təmizlə, yalnız hərf və rəqəmləri saxla
                const cleanTerm = term.replace(/[^a-zA-Z0-9]/g, '');
                
                if (cleanTerm.length > 1) {
                    // Böyük-kiçik hərfə həssas olmayan və xüsusi simvolları nəzərə almayan regex
                    // Hər bir hərf və ya rəqəm arasında istənilən xüsusi simvol ola bilər
                    const escapedTerm = cleanTerm.split('').map(char => {
                        return char.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                    }).join('[^a-zA-Z0-9]*');
                    
                    const regex = new RegExp(`(${escapedTerm})`, 'gi');
                    
                    // Əgər hüceyrədə axtarış sözü varsa
                    if (regex.test(cellHtml)) {
                        // Axtarış sözünü vurğula
                        cellHtml = cellHtml.replace(regex, '<span class="highlight-term">$1</span>');
                    }
                }
            });
            
            // Əgər dəyişiklik olubsa, HTML-i yenilə
            if (cellHtml !== originalText) {
                cell.innerHTML = cellHtml;
            }
        });
    }
}

// Səhifə yükləndikdə axtarış sözlərini vurğula
document.addEventListener('DOMContentLoaded', function() {
    highlightSearchTerms();
});