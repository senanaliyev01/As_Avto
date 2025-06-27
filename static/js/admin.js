function toggleStatistics() {
    var container = document.getElementById('statisticsContainer');
    var button = document.querySelector('.show-stats-btn');
    
    if (container.style.display === 'none' || container.style.display === '') {
        container.style.display = 'block';
        button.innerHTML = '<i class="fas fa-times"></i> Statistikanı Gizlət';
    } else {
        container.style.display = 'none';
        button.innerHTML = '<i class="fas fa-chart-bar"></i> İstifadəçi Statistikasına Bax';
    }
}

let searchTimeout = null;

// Mətni təmizləmək üçün funksiya
function cleanText(text) {
    // Yalnız hərflər, rəqəmlər, Azərbaycan hərfləri və "_" simvoluna icazə ver
    return text.replace(/[^a-zA-Z0-9əƏçÇşŞöÖğĞüÜıİ_]/g, '').toLowerCase();
}

// İki mətni müqayisə etmək üçün funksiya
function compareTexts(text1, text2) {
    const cleanText1 = cleanText(text1);
    const cleanText2 = cleanText(text2);
    
    // Tam uyğunluq
    if (cleanText1 === cleanText2) return 2;
    // Hissəvi uyğunluq
    if (cleanText2.includes(cleanText1)) return 1;
    // Uyğunsuzluq
    return 0;
}

function filterUsers() {
    clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(() => {
        const input = document.getElementById('userSearch');
        const searchText = input.value;
        const cleanSearchText = cleanText(searchText);
        const table = document.querySelector('.stats-table');
        const tr = table.getElementsByTagName('tr');
        const clearButton = document.querySelector('.clear-search');
        const noResults = document.querySelector('.no-results');
        let hasResults = false;
        let matches = [];

        // Təmizlə düyməsini göstər/gizlət
        clearButton.style.display = searchText ? 'block' : 'none';

        // Əgər axtarış mətni boşdursa
        if (!cleanSearchText) {
            for (let i = 1; i < tr.length; i++) {
                tr[i].style.display = '';
                const td = tr[i].getElementsByTagName('td')[0];
                if (td) td.innerHTML = td.textContent; // Highlight-ları təmizlə
            }
            noResults.style.display = 'none';
            return;
        }

        // Bütün sətirləri yoxla və uyğunluq dərəcəsini hesabla
        for (let i = 1; i < tr.length; i++) {
            const td = tr[i].getElementsByTagName('td')[0];
            if (td) {
                const originalText = td.textContent || td.innerText;
                const matchLevel = compareTexts(cleanSearchText, originalText);
                
                if (matchLevel > 0) {
                    matches.push({
                        row: tr[i],
                        cell: td,
                        text: originalText,
                        level: matchLevel
                    });
                    hasResults = true;
                } else {
                    tr[i].style.display = 'none';
                }
            }
        }

        // Nəticələri uyğunluq dərəcəsinə görə sırala
        matches.sort((a, b) => b.level - a.level);

        // Nəticələri göstər
        matches.forEach(match => {
            match.row.style.display = '';
            
            // Axtarış sözünü highlight et
            let displayText = match.text;
            const searchTerms = cleanSearchText.split('_').filter(Boolean); // "_" simvolu ilə ayrılmış sözləri al
            
            searchTerms.forEach(term => {
                const regex = new RegExp(`(${term})`, 'gi');
                displayText = displayText.replace(regex, '<span class="highlight">$1</span>');
            });
            
            match.cell.innerHTML = displayText;
        });

        // "Nəticə tapılmadı" mesajını göstər/gizlət
        noResults.style.display = !hasResults && searchText ? 'block' : 'none';
    }, 300);
}

function clearSearch() {
    const input = document.getElementById('userSearch');
    input.value = '';
    filterUsers();
    input.focus();
}

// Event listener-ləri əlavə et
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('userSearch');
    
    // Enter düyməsinə basıldıqda səhifənin yenilənməsinin qarşısını al
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
        }
    });

    // Input-a focus olduqda bütün mətni seç
    input.addEventListener('focus', function() {
        if (this.value) {
            this.select();
        }
    });

    // Input-a yazıldıqda avtomatik böyük hərfə çevir və yalnız icazə verilən simvolları saxla
    input.addEventListener('input', function() {
        let value = this.value.toUpperCase();
        // Yalnız hərflər, rəqəmlər, Azərbaycan hərfləri və "_" simvoluna icazə ver
        value = value.replace(/[^A-ZƏÇŞÖĞÜİ0-9_]/g, '');
        this.value = value;
    });

    // Sidebar aktiv link vurğusu
    document.querySelectorAll('.sidebar-item').forEach(function(item) {
        item.addEventListener('click', function() {
            document.querySelectorAll('.sidebar-item').forEach(function(i) {
                i.classList.remove('active');
            });
            item.classList.add('active');
        });
    });

    // Responsive sidebar toggle
    const sidebar = document.querySelector('.admin-sidebar');
    const main = document.querySelector('.admin-main');
    let sidebarOpen = true;
    function toggleSidebar() {
        if (window.innerWidth <= 900) {
            if (sidebarOpen) {
                sidebar.style.width = '60px';
                main.style.marginLeft = '60px';
                sidebarOpen = false;
            } else {
                sidebar.style.width = '240px';
                main.style.marginLeft = '240px';
                sidebarOpen = true;
            }
        }
    }
    if (!document.getElementById('sidebarToggleBtn')) {
        const btn = document.createElement('button');
        btn.id = 'sidebarToggleBtn';
        btn.innerHTML = '<i class="fas fa-bars"></i>';
        btn.style.position = 'fixed';
        btn.style.top = '18px';
        btn.style.left = '18px';
        btn.style.zIndex = '200';
        btn.style.background = '#2B5173';
        btn.style.color = '#fff';
        btn.style.border = 'none';
        btn.style.borderRadius = '6px';
        btn.style.width = '38px';
        btn.style.height = '38px';
        btn.style.display = 'none';
        btn.style.alignItems = 'center';
        btn.style.justifyContent = 'center';
        btn.style.fontSize = '1.3rem';
        btn.style.cursor = 'pointer';
        document.body.appendChild(btn);
        btn.addEventListener('click', toggleSidebar);
    }
    function checkSidebarBtn() {
        const btn = document.getElementById('sidebarToggleBtn');
        if (window.innerWidth <= 900) {
            btn.style.display = 'flex';
            sidebar.style.width = '60px';
            main.style.marginLeft = '60px';
            sidebarOpen = false;
        } else {
            btn.style.display = 'none';
            sidebar.style.width = '240px';
            main.style.marginLeft = '240px';
            sidebarOpen = true;
        }
    }
    window.addEventListener('resize', checkSidebarBtn);
    checkSidebarBtn();

    // Button click effektləri
    document.querySelectorAll('.btn, button').forEach(function(btn) {
        btn.addEventListener('mousedown', function() {
            btn.style.transform = 'scale(0.97)';
        });
        btn.addEventListener('mouseup', function() {
            btn.style.transform = 'scale(1)';
        });
        btn.addEventListener('mouseleave', function() {
            btn.style.transform = 'scale(1)';
        });
    });

    // === Modal funksionallığı ===
    initializeModal();
    initializeImageModal();
    initializeDetailsModal();
    initializeUserDetailsModal();
    // Əlavə olaraq showMessage funksiyası
});

// Modal açıb-bağlama funksiyası (base.js-dən)
function initializeModal() {
    const modal = document.getElementById('quantityModal');
    const closeBtn = document.querySelector('.close');
    const form = document.getElementById('addToCartForm');
    const modalContent = document.querySelector('.custom-quantity-modal-content');
    if (modal && closeBtn && form && modalContent) {
        closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const url = this.action;
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showMessage('success', data.message);
                    if (data.cart_count !== undefined) {
                        updateCartCounter(data.cart_count);
                    }
                    modal.style.display = 'none';
                } else {
                    showMessage('error', data.message);
                }
            })
            .catch(error => {
                showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
            });
        });
    }
}

// Şəkil modalı funksiyası (base.js-dən)
function initializeImageModal() {
    const modal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.image-modal-close');
    if (modal && closeBtn) {
        closeBtn.onclick = closeImageModal;
        modal.onclick = function(e) {
            if (e.target === modal) {
                closeImageModal();
            }
        };
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeImageModal();
            }
        });
    }
}
function openImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    if (modal && modalImg && imageSrc) {
        modalImg.src = imageSrc;
        modal.style.display = 'block';
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    }
}
function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// Details Modal funksiyası (base.js-dən)
function initializeDetailsModal() {
    const modal = document.getElementById('detailsModal');
    const closeBtn = document.querySelector('.details-modal-close');
    if (modal && closeBtn) {
        closeBtn.onclick = closeDetailsModal;
        modal.onclick = function(e) {
            if (e.target === modal) {
                closeDetailsModal();
            }
        };
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeDetailsModal();
            }
        });
    }
}
function openDetailsModal(productId) {
    const modal = document.getElementById('detailsModal');
    if (!modal) return;
    fetch(`/product-details/${productId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('detailsImage').src = data.product.sekil_url;
                document.getElementById('detailsName').textContent = data.product.adi;
                document.getElementById('detailsCategory').textContent = data.product.kateqoriya || '-';
                document.getElementById('detailsFirma').textContent = data.product.firma;
                document.getElementById('detailsAvtomobil').textContent = data.product.avtomobil;
                document.getElementById('detailsBrendKod').textContent = data.product.brend_kod;
                document.getElementById('detailsOlcu').textContent = data.product.olcu || '-';
                document.getElementById('detailsQiymet').textContent = data.product.qiymet + ' ₼';
                document.getElementById('detailsStok').textContent = data.product.stok + ' ədəd';
                document.getElementById('detailsMelumat').textContent = data.product.melumat || '-';
                const detailsSeller = document.getElementById('detailsSeller');
                if (detailsSeller) {
                    if (data.product.sahib_id && data.product.sahib_username) {
                        detailsSeller.innerHTML = `<a href="#" class="seller-link" onclick="openUserDetailsModal(${data.product.sahib_id}); return false;"><i class="fas fa-user"></i> ${data.product.sahib_username}</a>`;
                    } else {
                        detailsSeller.textContent = 'AS-AVTO';
                    }
                }
                modal.style.display = 'block';
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
            } else {
                showMessage('error', data.message);
            }
        })
        .catch(error => {
            showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        });
}
function closeDetailsModal() {
    const modal = document.getElementById('detailsModal');
    if (!modal) return;
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// User Details Modal funksiyası (base.js-dən)
function initializeUserDetailsModal() {
    const modal = document.getElementById('userDetailsModal');
    const closeBtn = document.querySelector('.user-details-modal-close');
    if (modal && closeBtn) {
        closeBtn.onclick = closeUserDetailsModal;
        modal.onclick = function(e) {
            if (e.target === modal) {
                closeUserDetailsModal();
            }
        };
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeUserDetailsModal();
            }
        });
    }
}
function openUserDetailsModal(userId) {
    const modal = document.getElementById('userDetailsModal');
    if (!modal) return;
    fetch(`/user-details/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('userDetailsUsername').textContent = data.user.username;
                document.getElementById('userDetailsPhone').textContent = data.user.phone || '-';
                document.getElementById('userDetailsAddress').textContent = data.user.address || '-';
                var img = document.getElementById('userDetailsImage');
                if (img && data.user.sekil_url) {
                    img.src = data.user.sekil_url;
                } else if (img) {
                    img.src = '/static/images/no_image.jpg';
                }
                modal.style.display = 'block';
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
            } else {
                showMessage('error', data.message);
            }
        })
        .catch(error => {
            showMessage('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        });
}
function closeUserDetailsModal() {
    const modal = document.getElementById('userDetailsModal');
    if (!modal) return;
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

// showMessage funksiyası (base.js-dən)
function showMessage(type, message) {
    const messagesContainer = document.createElement('div');
    messagesContainer.className = 'messages';
    messagesContainer.style.position = 'fixed';
    messagesContainer.style.top = '20px';
    messagesContainer.style.right = '-300px';
    messagesContainer.style.zIndex = '9999';
    messagesContainer.style.width = '300px';
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    messageDiv.appendChild(icon);
    messageDiv.appendChild(document.createTextNode(' ' + message));
    messagesContainer.appendChild(messageDiv);
    document.body.appendChild(messagesContainer);
    setTimeout(() => {
        messagesContainer.style.transition = 'right 0.5s ease';
        messagesContainer.style.right = '20px';
    }, 100);
    setTimeout(() => {
        messagesContainer.style.right = '-300px';
        setTimeout(() => messagesContainer.remove(), 500);
    }, 3000);
}

// Əlavə köməkçi funksiyalar
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function updateCartCounter(count) {
    const counter = document.querySelector('.cart-counter');
    if (counter) {
        counter.textContent = count;
    }
}

// Excel Import Modal Functions
document.addEventListener('DOMContentLoaded', function() {
    initializeExcelModal();
});

function initializeExcelModal() {
    var modal = document.getElementById('excelImportModal');
    var btn = document.getElementById('showExcelImportModal');
    var span = document.getElementsByClassName('close')[0];
    var closeBtn = document.getElementsByClassName('closeBtn')[0];

    if (!modal || !btn) {
        console.log('Modal elements not found');
        return;
    }

    // Modal açma düyməsi
    btn.addEventListener('click', function() {
        modal.style.display = "block";
    });

    // X düyməsi ilə bağlama
    if (span) {
        span.addEventListener('click', function() {
            modal.style.display = "none";
        });
    }

    // Bağla düyməsi ilə bağlama
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = "none";
        });
    }

    // Modal xaricində kliklə bağlama
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {
    // Cədvəldəki borc məbləğlərini yoxla və sinif əlavə et
    document.querySelectorAll('.stats-table .debt').forEach(cell => {
        const amount = parseFloat(cell.textContent.replace('₼', '').trim());
        if (amount > 0) {
            cell.classList.add('positive');
        } else if (amount < 0) {
            cell.classList.add('negative');
        } else {
            cell.classList.add('zero');
        }
    });

    // Ümumi statistikadakı borc məbləğini yoxla və sinif əlavə et
    const totalDebtItem = document.querySelector('.stats-item.debt');
    const totalDebtAmount = parseFloat(totalDebtItem.querySelector('span').textContent.replace('₼', '').trim());
    
    if (totalDebtAmount > 0) {
        totalDebtItem.classList.add('positive');
    } else if (totalDebtAmount < 0) {
        totalDebtItem.classList.add('negative');
    } else {
        totalDebtItem.classList.add('zero');
    }
});