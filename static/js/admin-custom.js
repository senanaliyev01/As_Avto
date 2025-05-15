// Admin paneli üçün xüsusi JavaScript - Məhsul cədvəli funksionallığı

document.addEventListener('DOMContentLoaded', function() {
    // Cədvəl sətirlərinə hover hadisəsi əlavə et
    setupTableRowHover();
    
    // Axtarış funksiyasını təkmilləşdir
    enhanceSearchExperience();
    
    // Filterlər panelini təkmilləşdir
    enhanceFilterPanel();
    
    // Məhsullara klikləmək üçün funksionallıq
    setupRowClicks();
    
    // Stok sütunu üçün rəng indikatorunu əlavə et
    enhanceStockColumn();
    
    // Responsiv dizayn üçün sütunları idarə et
    handleResponsiveColumns();
    
    // Excel modal funksionallığını inkişaf etdir
    enhanceExcelModal();
});

// Cədvəl sətirlərinin hover effekti
function setupTableRowHover() {
    if (!document.querySelector('#result_list')) return;
    
    const rows = document.querySelectorAll('#result_list tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'background-color 0.2s';
        });
    });
}

// Axtarış funksiyasını təkmilləşdirmək
function enhanceSearchExperience() {
    const searchbar = document.querySelector('#searchbar');
    if (!searchbar) return;
    
    // Placeholder əlavə et
    searchbar.setAttribute('placeholder', 'Məhsul adı, brend kodu və ya OEM ilə axtarış edin...');
    
    // Axtarış nəticələrini vurğulamaq üçün funksiya
    searchbar.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length < 2) return;
        
        // Nəticələri vurğula
        highlightSearchResults(query);
    });
}

// Axtarış nəticələrini vurğulamaq
function highlightSearchResults(query) {
    const cells = document.querySelectorAll('#result_list tbody td');
    
    cells.forEach(cell => {
        const originalText = cell.textContent;
        const lowerText = originalText.toLowerCase();
        
        if (lowerText.includes(query)) {
            const startIndex = lowerText.indexOf(query);
            const endIndex = startIndex + query.length;
            
            // HTML-i təmizlə və mətni təzədən format elə
            if (!cell.hasAttribute('data-original-text')) {
                cell.setAttribute('data-original-text', originalText);
            }
            
            // Vurğulama
            const before = originalText.substring(0, startIndex);
            const match = originalText.substring(startIndex, endIndex);
            const after = originalText.substring(endIndex);
            
            cell.innerHTML = before + '<span class="highlight">' + match + '</span>' + after;
        } else if (cell.hasAttribute('data-original-text')) {
            // Əgər əvvəl vurğulanıbsa, original mətnə qaytar
            cell.innerHTML = cell.getAttribute('data-original-text');
        }
    });
}

// Filterlər panelini təkmilləşdirmək
function enhanceFilterPanel() {
    const filterHeaders = document.querySelectorAll('#changelist-filter h3');
    
    filterHeaders.forEach(header => {
        // Toggle ikonu əlavə et
        const toggleIcon = document.createElement('span');
        toggleIcon.innerHTML = '&#9660;';
        toggleIcon.style.float = 'right';
        toggleIcon.style.cursor = 'pointer';
        toggleIcon.style.transition = 'transform 0.3s';
        
        header.appendChild(toggleIcon);
        
        // Klikləmə hadisəsi
        header.addEventListener('click', function() {
            const list = this.nextElementSibling;
            
            if (list.style.display === 'none') {
                list.style.display = 'block';
                toggleIcon.style.transform = 'rotate(0deg)';
            } else {
                list.style.display = 'none';
                toggleIcon.style.transform = 'rotate(-90deg)';
            }
        });
    });
}

// Sıra klikləməni qurmaq
function setupRowClicks() {
    const rows = document.querySelectorAll('#result_list tbody tr');
    
    rows.forEach(row => {
        row.style.cursor = 'pointer';
        
        row.addEventListener('click', function(e) {
            // Əgər checkbox-a və ya linkə klik olunubsa, redirekt etmə
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            // Redakt səhifəsinə keç
            const editUrl = this.querySelector('.field-adi a').getAttribute('href');
            if (editUrl) {
                window.location.href = editUrl;
            }
        });
    });
}

// Stok sütununu təkmilləşdirmək
function enhanceStockColumn() {
    const stockCells = document.querySelectorAll('.field-get_stok span, .field-stok');
    
    stockCells.forEach(cell => {
        const stockValue = parseInt(cell.textContent.trim());
        
        // Əgər artıq formatlaşdırılıbsa, keç
        if (cell.classList.contains('status-pill')) return;
        
        // Status sinifi əlavə et
        cell.classList.add('status-pill');
        
        if (stockValue > 10) {
            cell.classList.add('high-stock');
        } else if (stockValue > 0) {
            cell.classList.add('medium-stock');
        } else {
            cell.classList.add('low-stock');
        }
    });
}

// Responsiv sütunları idarə et
function handleResponsiveColumns() {
    function adjustColumns() {
        const windowWidth = window.innerWidth;
        const headers = document.querySelectorAll('#result_list thead th');
        const allRows = document.querySelectorAll('#result_list tbody tr');
        
        // Ekran ölçüsünə görə sütunları gizlət/göstər
        if (windowWidth < 768) {
            // Mobil görünüş - minimal sütunlar
            headers.forEach((header, index) => {
                // Əsas sütunları saxla, digərlərini gizlət
                const isMainColumn = header.classList.contains('field-adi') || 
                                    header.classList.contains('field-get_qiymet') || 
                                    header.classList.contains('field-get_stok');
                
                if (!isMainColumn && index > 0) {
                    header.style.display = 'none';
                    allRows.forEach(row => {
                        if (row.cells[index]) {
                            row.cells[index].style.display = 'none';
                        }
                    });
                }
            });
        } else if (windowWidth < 992) {
            // Tablet görünüş - orta səviyyəli sütunlar
            headers.forEach((header, index) => {
                header.style.display = '';
                allRows.forEach(row => {
                    if (row.cells[index]) {
                        row.cells[index].style.display = '';
                    }
                });
                
                // Bəzi az əhəmiyyətli sütunları gizlət
                const isSecondaryColumn = header.classList.contains('field-get_melumat') || 
                                        header.classList.contains('field-get_olcu') || 
                                        header.classList.contains('field-get_oem');
                
                if (isSecondaryColumn) {
                    header.style.display = 'none';
                    allRows.forEach(row => {
                        if (row.cells[index]) {
                            row.cells[index].style.display = 'none';
                        }
                    });
                }
            });
        } else {
            // Desktop görünüş - bütün sütunlar
            headers.forEach((header, index) => {
                header.style.display = '';
                allRows.forEach(row => {
                    if (row.cells[index]) {
                        row.cells[index].style.display = '';
                    }
                });
            });
        }
    }
    
    // İlk yükləmədə sütunları tənzimlə
    adjustColumns();
    
    // Ekran ölçüsü dəyişdikdə sütunları tənzimlə
    window.addEventListener('resize', adjustColumns);
}

// Excel modal pəncərəsini təkmilləşdir
function enhanceExcelModal() {
    const excelModalBtn = document.getElementById('showExcelImportModal');
    if (!excelModalBtn) return;
    
    const modal = document.getElementById('excelImportModal');
    const closeBtn = modal.querySelector('.close');
    const closeBtnBottom = modal.querySelector('.closeBtn');
    
    // Modal açılma funksiyası
    excelModalBtn.addEventListener('click', function() {
        modal.style.display = 'block';
        modal.classList.add('fade-in');
        document.body.style.overflow = 'hidden';
    });
    
    // Modal bağlanma funksiyaları
    closeBtn.addEventListener('click', closeModal);
    closeBtnBottom.addEventListener('click', closeModal);
    
    // Modal xaricindəki kliklər
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Modal bağlanma funksiyası
    function closeModal() {
        modal.classList.add('fade-out');
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade-in', 'fade-out');
            document.body.style.overflow = '';
        }, 300);
    }
    
    // Excel faylı seçimi
    const fileInput = modal.querySelector('input[type="file"]');
    fileInput.addEventListener('change', function() {
        const fileName = this.files[0] ? this.files[0].name : 'Fayl seçilməyib';
        const fileLabel = document.createElement('div');
        fileLabel.textContent = 'Seçilmiş fayl: ' + fileName;
        fileLabel.style.marginTop = '10px';
        fileLabel.style.color = '#444';
        
        // Əvvəlki etiketləri təmizlə
        const prevLabels = this.parentElement.querySelectorAll('div');
        prevLabels.forEach(label => label.remove());
        
        this.parentElement.appendChild(fileLabel);
    });
} 