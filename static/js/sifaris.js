document.addEventListener('DOMContentLoaded', function() {
    // Hover effektləri
    const addHoverEffect = (elements, scaleAmount = 1.02) => {
        elements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.transform = `scale(${scaleAmount})`;
                element.style.zIndex = '1';
            });
            element.addEventListener('mouseleave', () => {
                element.style.transform = 'scale(1)';
                element.style.zIndex = '0';
            });
        });
    };

    // Cədvəl sətirləri üçün hover
    addHoverEffect(document.querySelectorAll('tbody tr'), 1.01);

    // Status badge-ləri üçün hover
    addHoverEffect(document.querySelectorAll('.status-badge'), 1.05);

    // Statistika kartları üçün hover
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 15px 30px rgba(0,0,0,0.15)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--shadow-lg)';
        });
    });

    // Scroll animasiyası
    const scrollElements = document.querySelectorAll('.stat-item, .table-container, .info-row');
    
    const elementInView = (el, percentageScroll = 100) => {
        const elementTop = el.getBoundingClientRect().top;
        return (
            elementTop <= 
            ((window.innerHeight || document.documentElement.clientHeight) * (percentageScroll/100))
        );
    };

    const displayScrollElement = element => {
        element.classList.add('active');
    };

    const handleScrollAnimation = () => {
        scrollElements.forEach((el) => {
            if (elementInView(el, 90)) {
                displayScrollElement(el);
            }
        });
    };

    // Scroll event
    window.addEventListener('scroll', () => {
        handleScrollAnimation();
    });

    // İlk yükləmə
    handleScrollAnimation();

    // Status badge-ləri üçün pulsing effekt
    const badges = document.querySelectorAll('.status-badge');
    badges.forEach(badge => {
        setInterval(() => {
            badge.style.transform = 'scale(1.05)';
            setTimeout(() => {
                badge.style.transform = 'scale(1)';
            }, 200);
        }, 3000);
    });

    // Cədvəl sıralama
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        const tbody = table.querySelector('tbody');
        Array.from(tbody.querySelectorAll('tr'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => tbody.appendChild(tr));
    })));
}); 

   // Səhifə yükləndikdə
   document.addEventListener('DOMContentLoaded', function() {
    // Browser-in geri düyməsini deaktiv et
    window.history.pushState(null, '', window.location.href);
    window.onpopstate = function() {
        window.history.pushState(null, '', window.location.href);
    };
});

function createSmoke(truckContainer) {
    const smoke = document.createElement('div');
    smoke.className = 'smoke';
    truckContainer.appendChild(smoke);
    
    setTimeout(() => {
        smoke.remove();
    }, 2000);
}

// Tüstü effektini başlat
document.querySelectorAll('.truck-container').forEach(container => {
    setInterval(() => {
        createSmoke(container);
    }, 300);
});

// Progress Tracker Animasiyaları
function initProgressTracker() {
    const steps = document.querySelectorAll('.progress-step');
    
    steps.forEach((step, index) => {
        if (step.classList.contains('active')) {
            setTimeout(() => {
                // İkon animasiyası
                const icon = step.querySelector('.step-icon');
                if (icon) {
                    icon.style.transform = 'scale(1.1)';
                    icon.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                }
                
                // Check ikonu animasiyası
                const check = step.querySelector('.step-check');
                if (check) {
                    check.style.opacity = '0';
                    check.style.transform = 'scale(0)';
                    
                    setTimeout(() => {
                        check.style.opacity = '1';
                        check.style.transform = 'scale(1)';
                    }, 200);
                }
                
                // Progress line animasiyası
                const nextLine = step.nextElementSibling;
                if (nextLine && nextLine.classList.contains('progress-line')) {
                    nextLine.style.background = 'linear-gradient(90deg, #64ffda, #0a192f)';
                    nextLine.style.transition = 'background 0.5s ease';
                }
                
                // İkon rəng animasiyası
                const mainIcon = step.querySelector('.step-main-icon');
                if (mainIcon) {
                    mainIcon.style.color = '#64ffda';
                    mainIcon.style.transition = 'color 0.3s ease';
                }
                
                // Başlıq animasiyası
                const title = step.querySelector('.step-title');
                if (title) {
                    title.style.color = '#64ffda';
                    title.style.transition = 'color 0.3s ease';
                }
            }, index * 300);
        }
    });
}

// Səhifə yükləndikdə
document.addEventListener('DOMContentLoaded', function() {
    initProgressTracker();
    
    // Hover effektləri
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach(step => {
        step.addEventListener('mouseenter', () => {
            if (step.classList.contains('active')) {
                const icon = step.querySelector('.step-icon');
                if (icon) {
                    icon.style.transform = 'scale(1.15)';
                }
            }
        });
        
        step.addEventListener('mouseleave', () => {
            if (step.classList.contains('active')) {
                const icon = step.querySelector('.step-icon');
                if (icon) {
                    icon.style.transform = 'scale(1.1)';
                }
            }
        });
    });
});

// Success check ikonları üçün animasiya
document.querySelectorAll('.success-check-icon').forEach(icon => {
    icon.addEventListener('mouseover', () => {
        icon.classList.add('tada');
    });
    
    icon.addEventListener('mouseout', () => {
        icon.classList.remove('tada');
    });
});
