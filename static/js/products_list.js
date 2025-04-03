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
        // Orijinal axtarış mətni
        const originalSearchText = searchText.trim();
        
        // Cədvəldəki bütün mətn hüceyrələrini seç
        const tableCells = document.querySelectorAll('.products-table tbody td');
        
        // Bütün hüceyrələri yoxla
        tableCells.forEach(cell => {
            const cellText = cell.textContent.trim();
            
            // Xüsusi simvol və boşluqları daxil olmaqla  axtarış 
            if (cellText.toLowerCase().includes(originalSearchText.toLowerCase())) {
                // Bu üsulla escape edərək təhlükəsiz regex yaradırıq
                const safeSearchText = escapeRegExp(originalSearchText);
                const regex = new RegExp(`(${safeSearchText})`, 'gi');
                
                // Orijinal formatla əvəz edərək vurğulayırıq
                cell.innerHTML = cellText.replace(regex, '<span class="highlight-term">$1</span>');
            } else {
                // Axtarış mətninə tire və boşluqları silərək yoxlamaq
                const cleanSearchText = originalSearchText.replace(/[\s\-_!@#$%^&*()+=,.?":;{}|<>\/\\[\]]/g, '');
                const cleanCellText = cellText.replace(/[\s\-_!@#$%^&*()+=,.?":;{}|<>\/\\[\]]/g, '');
                
                if (cleanSearchText.length > 2 && cleanCellText.toLowerCase().includes(cleanSearchText.toLowerCase())) {
                    // Orijinal mətndə pozisiyasını tapmaq
                    let index = cleanCellText.toLowerCase().indexOf(cleanSearchText.toLowerCase());
                    
                    if (index !== -1) {
                        // Xüsusi simvolları nəzərə alaraq orijinal mətndə pozisiyanı tapmaq üçün əlavə hesablamalar
                        let startPosInOriginal = 0;
                        let cleanCharCount = 0;
                        
                        for (let i = 0; i < cellText.length; i++) {
                            const char = cellText[i];
                            if (!/[\s\-_!@#$%^&*()+=,.?":;{}|<>\/\\[\]]/.test(char)) {
                                cleanCharCount++;
                            }
                            
                            if (cleanCharCount > index) {
                                startPosInOriginal = i - (cleanCharCount - index) + 1;
                                break;
                            }
                        }
                        
                        // Vurğulanacaq mətn uzunluğunu hesabla
                        let endPosInOriginal = startPosInOriginal;
                        let highlightedChars = 0;
                        
                        for (let i = startPosInOriginal; i < cellText.length; i++) {
                            const char = cellText[i];
                            if (!/[\s\-_!@#$%^&*()+=,.?":;{}|<>\/\\[\]]/.test(char)) {
                                highlightedChars++;
                            }
                            
                            endPosInOriginal = i;
                            
                            if (highlightedChars >= cleanSearchText.length) {
                                break;
                            }
                        }
                        
                        // Mətni hissələrə bölüb vurğulama əlavə et
                        const beforeText = cellText.substring(0, startPosInOriginal);
                        const highlightedText = cellText.substring(startPosInOriginal, endPosInOriginal + 1);
                        const afterText = cellText.substring(endPosInOriginal + 1);
                        
                        cell.innerHTML = beforeText + 
                                        '<span class="highlight-term">' + 
                                        highlightedText + 
                                        '</span>' + 
                                        afterText;
                    }
                }
            }
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