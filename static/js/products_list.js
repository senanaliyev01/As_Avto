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
    const combinedSearchText = urlParams.get('combined_search_text');
    const hyphenatedSearchText = urlParams.get('hyphenated_search_text');
    
    // Bütün axtarış sözlərini bir massivdə topla
    const searchTerms = [];
    
    // Əsas axtarış sözünü əlavə et
    if (searchText && searchText.trim() !== '') {
        searchTerms.push(searchText.trim());
    }
    
    // Birləşik versiyanı əlavə et
    if (combinedSearchText && combinedSearchText.trim() !== '') {
        searchTerms.push(combinedSearchText.trim());
    }
    
    // Tire ilə versiyanı əlavə et
    if (hyphenatedSearchText && hyphenatedSearchText.trim() !== '') {
        searchTerms.push(hyphenatedSearchText.trim());
    }
    
    // Əgər heç bir axtarış sözü yoxdursa, çıx
    if (searchTerms.length === 0) {
        return;
    }
    
    // Cədvəldəki bütün mətn hüceyrələrini seç
    const tableCells = document.querySelectorAll('.products-table tbody td:not(:first-child):not(:last-child):not(:nth-last-child(2))');
    
    // Hər bir hüceyrə üçün
    tableCells.forEach(cell => {
        const originalText = cell.textContent;
        let newText = originalText;
        
        // Hər bir axtarış sözü üçün
        searchTerms.forEach(term => {
            // Böyük-kiçik hərfə həssas olmayan regex
            const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
            
            // Əgər hüceyrədə axtarış sözü varsa
            if (regex.test(newText)) {
                // Axtarış sözünü vurğula
                newText = newText.replace(regex, '<span class="highlight-term">$1</span>');
            }
            
            // Əgər axtarış sözü tire ilə yazılıbsa, birləşik versiyasını da yoxla
            if (term.includes('-')) {
                const combinedTerm = term.replace(/-/g, '');
                const combinedRegex = new RegExp(`(${escapeRegExp(combinedTerm)})`, 'gi');
                
                if (combinedRegex.test(newText)) {
                    newText = newText.replace(combinedRegex, '<span class="highlight-term">$1</span>');
                }
            }
            
            // Əgər axtarış sözü birləşikdirsə, tire ilə versiyasını da yoxla
            if (/[A-Za-z]+[0-9]+/.test(term)) {
                const hyphenatedTerm = term.replace(/([A-Za-z]+)([0-9]+)/g, '$1-$2');
                const hyphenatedRegex = new RegExp(`(${escapeRegExp(hyphenatedTerm)})`, 'gi');
                
                if (hyphenatedRegex.test(newText)) {
                    newText = newText.replace(hyphenatedRegex, '<span class="highlight-term">$1</span>');
                }
            }
        });
        
        // Əgər mətn dəyişibsə, yeni mətni təyin et
        if (newText !== originalText) {
            cell.innerHTML = newText;
        }
    });
}

// RegExp xüsusi simvollarını qaçırmaq üçün funksiya
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Səhifə yükləndikdə axtarış sözlərini vurğula
document.addEventListener('DOMContentLoaded', function() {
    highlightSearchTerms();
});