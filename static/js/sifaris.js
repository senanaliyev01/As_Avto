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

function createSmokeParticle(container, type) {
    const smoke = document.createElement('div');
    smoke.className = 'smoke-particle';
   
    // Təsadüfi ölçü
    const size = Math.random() * 6 + 4;
    smoke.style.width = size + 'px';
    smoke.style.height = size + 'px';
   
    if (type === 'exhaust') {
        smoke.style.animation = 'exhaustSmoke 2s forwards';
        container.appendChild(smoke);
        smoke.style.right = '-5px';
        smoke.style.bottom = '5px';
    } else if (type === 'wheel') {
        smoke.style.animation = 'wheelSmoke 1s forwards';
        container.appendChild(smoke);
        smoke.style.bottom = '-2px';
        smoke.style.right = Math.random() * 20 + 5 + 'px';
    }
   
    setTimeout(() => smoke.remove(), 2000);
}

function addWheels(truckContainer) {
    const wheelFront = document.createElement('div');
    wheelFront.className = 'wheel wheel-front';
   
    const wheelBack = document.createElement('div');
    wheelBack.className = 'wheel wheel-back';
   
    truckContainer.appendChild(wheelFront);
    truckContainer.appendChild(wheelBack);
}

function initTruckAnimations() {
    document.querySelectorAll('.truck-container').forEach(container => {
        addWheels(container);
       
        // Mühərrik tüstüsü
        setInterval(() => {
            createSmokeParticle(container, 'exhaust');
        }, 200);
       
        // Təkər tüstüsü
        setInterval(() => {
            createSmokeParticle(container, 'wheel');
        }, 300);
    });
}

function initStatusAnimations() {
    // Status ikonları üçün animasiyalar
    document.querySelectorAll('.status-badge').forEach(badge => {
        const status = badge.classList.toString().match(/status-(\w+)/)[1];
        const icon = badge.querySelector('i');
       
        if (icon) {
            switch(status) {
                case 'gozleyir':
                    icon.classList.add('clock-animation');
                    break;
                case 'hazirlanir':
                    icon.classList.add('box-animation');
                    break;
                case 'yoldadir':
                    // Kamaz animasiyaları avtomatik işləyir
                    break;
                case 'catdirildi':
                    icon.classList.add('check-animation');
                    break;
            }
        }
    });
}

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', function() {
    initTruckAnimations();
    initStatusAnimations();
   
    // Digər mövcud kodlar...
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