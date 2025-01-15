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

function createTruckElement() {
    const truckContainer = document.createElement('div');
    truckContainer.className = 'truck-container';

    // Kamaz ikonu
    const truckIcon = document.createElement('i');
    truckIcon.className = 'fas fa-truck truck-icon';
    truckContainer.appendChild(truckIcon);

    // Təkərlər
    const wheelFront = document.createElement('div');
    wheelFront.className = 'wheel wheel-front';
    const wheelBack = document.createElement('div');
    wheelBack.className = 'wheel wheel-back';
    truckContainer.appendChild(wheelFront);
    truckContainer.appendChild(wheelBack);

    // Təkər tüstüsü
    const wheelSmoke = document.createElement('div');
    wheelSmoke.className = 'wheel-smoke';
    for (let i = 0; i < 3; i++) {
        const smokeParticle = document.createElement('div');
        smokeParticle.className = 'wheel-smoke-particle';
        smokeParticle.style.animationDelay = `${i * 0.3}s`;
        wheelSmoke.appendChild(smokeParticle);
    }
    truckContainer.appendChild(wheelSmoke);

    // Əsas tüstü
    const exhaustSmoke = document.createElement('div');
    exhaustSmoke.className = 'exhaust-smoke';
    for (let i = 0; i < 5; i++) {
        const smokeParticle = document.createElement('div');
        smokeParticle.className = 'smoke-particle';
        smokeParticle.style.width = `${4 + i * 2}px`;
        smokeParticle.style.height = `${4 + i * 2}px`;
        smokeParticle.style.animationDelay = `${i * 0.2}s`;
        exhaustSmoke.appendChild(smokeParticle);
    }
    truckContainer.appendChild(exhaustSmoke);

    return truckContainer;
}

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', function() {
    // Mövcud truck containerləri yeniləri ilə əvəz et
    document.querySelectorAll('.status-yoldadir .icon-container').forEach(container => {
        const oldTruck = container.querySelector('.truck-container');
        if (oldTruck) {
            const newTruck = createTruckElement();
            container.replaceChild(newTruck, oldTruck);
        }
    });

    // Status animasiyalarını aktivləşdir
    const statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(badge => {
        if (badge.classList.contains('status-gozleyir')) {
            badge.querySelector('i').classList.add('pulse');
        } else if (badge.classList.contains('status-hazirlanir')) {
            badge.querySelector('i').classList.add('bounce');
        } else if (badge.classList.contains('status-catdirildi')) {
            badge.querySelector('i').classList.add('tada');
        }
    });
});
