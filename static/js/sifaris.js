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

// Progress addımlarını animasiya et
document.querySelectorAll('.progress-step').forEach((step, index) => {
    if (step.classList.contains('active')) {
        setTimeout(() => {
            step.style.transform = 'scale(1.1)';
            setTimeout(() => {
                step.style.transform = 'scale(1)';
            }, 200);
        }, index * 300);
    }
});

// Yol və ağacları yaratmaq üçün funksiya
function createShippingScene() {
    const shippingContainers = document.querySelectorAll('.status-shipping');
    
    shippingContainers.forEach(container => {
        const scene = document.createElement('div');
        scene.className = 'shipping-scene';
        
        // Yol əlavə et
        const road = document.createElement('div');
        road.className = 'road';
        
        // Ağacları əlavə et
        const trees = document.createElement('div');
        trees.className = 'trees';
        
        // 5 ağac əlavə et
        for(let i = 0; i < 5; i++) {
            const tree = document.createElement('div');
            tree.className = 'tree';
            tree.style.left = `${i * 40 + 20}px`;
            trees.appendChild(tree);
        }
        
        scene.appendChild(road);
        scene.appendChild(trees);
        container.appendChild(scene);
    });
}

// Status animasiyalarını aktivləşdirmək üçün
function activateStatusAnimations() {
    const currentStatus = document.querySelector('.progress-step.active');
    if (!currentStatus) return;
    
    // Bütün animasiyaları dayandır
    document.querySelectorAll('.status-icon-container').forEach(container => {
        container.style.opacity = '0.5';
    });
    
    // Aktiv statusun animasiyasını başlat
    const activeIcon = currentStatus.querySelector('.status-icon-container');
    if (activeIcon) {
        activeIcon.style.opacity = '1';
        activeIcon.style.transform = 'scale(1.1)';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    createShippingScene();
    activateStatusAnimations();
    
    // Hər 3 saniyədən bir tüstü effekti
    setInterval(() => {
        const activeTruck = document.querySelector('.progress-step.active .truck-icon');
        if (activeTruck) {
            const smoke = document.createElement('div');
            smoke.className = 'smoke-particle';
            activeTruck.appendChild(smoke);
            
            setTimeout(() => smoke.remove(), 2000);
        }
    }, 300);
});