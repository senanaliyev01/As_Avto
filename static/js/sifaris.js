document.addEventListener('DOMContentLoaded', function() {
    // Status ikonlarının animasiyalarını idarə et
    initializeStatusAnimations();
    
    // Cədvəl sətirlərinə hover effekti əlavə et
    initializeTableHoverEffects();
    
    // Statistika kartlarına hover effekti əlavə et
    initializeStatCardEffects();
    
    // Progress bar animasiyasını başlat
    initializeProgressBar();
});

function initializeStatusAnimations() {
    // Tüstü effekti üçün çoxlu element yaratma
    const truckContainers = document.querySelectorAll('.truck-container');
    truckContainers.forEach(container => {
        for (let i = 0; i < 3; i++) {
            const smoke = document.createElement('div');
            smoke.className = 'smoke';
            smoke.style.animationDelay = `${i * 0.4}s`;
            container.appendChild(smoke);
        }
    });
}

function initializeTableHoverEffects() {
    const tableRows = document.querySelectorAll('tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'scale(1.01)';
            row.style.transition = 'transform 0.3s ease';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'scale(1)';
        });
    });
}

function initializeStatCardEffects() {
    const statItems = document.querySelectorAll('.stat-item');
    
    statItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            // Parlama effekti
            const glow = document.createElement('div');
            glow.className = 'stat-glow';
            item.appendChild(glow);
            
            setTimeout(() => {
                glow.remove();
            }, 1000);
        });
    });
}

function initializeProgressBar() {
    const progressSteps = document.querySelectorAll('.progress-step');
    let delay = 0;
    
    progressSteps.forEach((step, index) => {
        if (step.classList.contains('active')) {
            setTimeout(() => {
                step.style.opacity = '0';
                step.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    step.style.opacity = '1';
                    step.style.transform = 'scale(1)';
                }, 200);
            }, delay);
            
            delay += 300;
        }
    });
}

// Səhifə yüklənərkən fade-in animasiyası
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
});

// Scroll zamanı elementlərin animasiyası
window.addEventListener('scroll', () => {
    const elements = document.querySelectorAll('.table-container, .sifaris-info, .statistic');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            if (!element.classList.contains('animated')) {
                element.classList.add('animated');
                element.style.animation = 'fadeInUp 0.5s ease forwards';
            }
        }
    });
});

// Fade-in-up animasiyası
const fadeInUpKeyframes = `
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}`;

// Stil əlavə et
const style = document.createElement('style');
style.textContent = fadeInUpKeyframes;
document.head.appendChild(style);

// Qiymət formatı
function formatCurrency(amount) {
    return parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Tarix formatı
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('az-AZ', options);
}

// Status rənglərini avtomatik yeniləmə
function updateStatusColors() {
    const statusBadges = document.querySelectorAll('.status-badge');
    
    statusBadges.forEach(badge => {
        const status = badge.classList[1].split('-')[1];
        let color;
        
        switch(status) {
            case 'gozleyir':
                color = '#FFC107';
                break;
            case 'hazirlanir':
                color = '#2196F3';
                break;
            case 'yoldadir':
                color = '#9C27B0';
                break;
            case 'catdirildi':
                color = '#4CAF50';
                break;
        }
        
        badge.style.borderColor = color;
    });
}

// Səhifə yüklənəndə status rənglərini yenilə
document.addEventListener('DOMContentLoaded', updateStatusColors);
