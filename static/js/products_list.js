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
        
        // Xüsusi simvolları təmizlə və birləşik versiyaları əlavə et
        const enhancedSearchTerms = [];
        searchTerms.forEach(term => {
            enhancedSearchTerms.push(term);
            
            // Əgər term rəqəm və ya simvollardan ibarətdirsə
            if (/[0-9\-]/.test(term)) {
                // Bütün tire və boşluqları silərək birləşik versiya əlavə et
                const combinedTerm = term.replace(/[\-\s]/g, '');
                if (combinedTerm !== term && combinedTerm.length > 1) {
                    enhancedSearchTerms.push(combinedTerm);
                }
                
                // Əgər term birləşikdirsə, tire ilə ayrılmış versiyasını əlavə et
                if (term.length >= 5 && !/[\-\s]/.test(term)) {
                    // Rəqəm ardıcıllıqlarını tire ilə ayır (məsələn 2630035504 -> 26300-35504)
                    const hyphenatedTerm = term.replace(/(\d{5})(\d{5})/g, '$1-$2')
                                              .replace(/(\d{4})(\d{4})/g, '$1-$2')
                                              .replace(/(\d{3})(\d{3})/g, '$1-$2');
                    if (hyphenatedTerm !== term) {
                        enhancedSearchTerms.push(hyphenatedTerm);
                    }
                }
            }
        });
        
        // Cədvəldəki bütün mətn hüceyrələrini seç
        const tableCells = document.querySelectorAll('.products-table tbody td:not(:first-child):not(:last-child):not(:nth-last-child(2))');
        
        // Hər bir hüceyrə üçün
        tableCells.forEach(cell => {
            const originalText = cell.textContent;
            let newText = originalText;
            
            // Hər bir axtarış sözü üçün
            enhancedSearchTerms.forEach(term => {
                // Böyük-kiçik hərfə həssas olmayan regex
                const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
                
                // Əgər hüceyrədə axtarış sözü varsa
                if (regex.test(newText)) {
                    // Axtarış sözünü vurğula
                    newText = newText.replace(regex, '<span class="highlight-term">$1</span>');
                }
            });
            
            // Əgər mətn dəyişibsə, yeni mətni təyin et
            if (newText !== originalText) {
                cell.innerHTML = newText;
            }
        });
        
        // Xüsusi olaraq brend_kod və oem sütunlarını yoxla
        const brendKodCells = document.querySelectorAll('.products-table tbody td:nth-child(5)'); // Brend Kod sütunu
        const oemCells = document.querySelectorAll('.products-table tbody td:nth-child(6)'); // OEM Kod sütunu
        
        // Brend kod və OEM kod sütunlarını xüsusi olaraq yoxla
        [brendKodCells, oemCells].forEach(cells => {
            cells.forEach(cell => {
                const originalText = cell.textContent.trim();
                let newText = originalText;
                
                // Orijinal axtarış mətni ilə birbaşa yoxla
                if (originalText.toLowerCase().includes(searchText.toLowerCase())) {
                    const regex = new RegExp(`(${escapeRegExp(searchText)})`, 'gi');
                    newText = originalText.replace(regex, '<span class="highlight-term">$1</span>');
                    cell.innerHTML = newText;
                    return;
                }
                
                // Əgər axtarış mətni rəqəm və ya simvollardan ibarətdirsə
                if (/[0-9\-]/.test(searchText)) {
                    // Boşluqları və xüsusi simvolları sil
                    const cleanSearchText = searchText.replace(/[^a-zA-Z0-9]/g, '');
                    const cleanCellText = originalText.replace(/[^a-zA-Z0-9]/g, '');
                    
                    if (cleanCellText.toLowerCase().includes(cleanSearchText.toLowerCase())) {
                        // Orijinal mətndə axtarış sözünü tap və vurğula
                        let startIndex = cleanCellText.toLowerCase().indexOf(cleanSearchText.toLowerCase());
                        let endIndex = startIndex + cleanSearchText.length;
                        
                        // Orijinal mətndə uyğun hissəni vurğula
                        let result = '';
                        let currentCleanIndex = 0;
                        
                        for (let i = 0; i < originalText.length; i++) {
                            const char = originalText[i];
                            if (/[a-zA-Z0-9]/.test(char)) {
                                if (currentCleanIndex >= startIndex && currentCleanIndex < endIndex) {
                                    // Vurğulanacaq hissə
                                    if (currentCleanIndex === startIndex) {
                                        result += '<span class="highlight-term">';
                                    }
                                    result += char;
                                    if (currentCleanIndex === endIndex - 1) {
                                        result += '</span>';
                                    }
                                } else {
                                    result += char;
                                }
                                currentCleanIndex++;
                            } else {
                                result += char;
                            }
                        }
                        
                        cell.innerHTML = result;
                    }
                }
            });
        });
    }
}

// RegExp xüsusi simvollarını qaçırmaq üçün funksiya
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Səhifə yükləndikdə axtarış sözlərini vurğula
document.addEventListener('DOMContentLoaded', function() {
    highlightSearchTerms();
});