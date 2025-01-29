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

    // Saat əqrəbinin fırlanması
    const clockIcon = document.querySelector('.gozleyir-icon .fa-clock');
    if (clockIcon) {
        let rotation = 0;
        setInterval(() => {
            rotation += 6;
            clockIcon.style.transform = `rotate(${rotation}deg)`;
        }, 100);
    }

    // Qutu animasiyası
    const boxIcon = document.querySelector('.hazirlanir-icon .fa-box-open');
    if (boxIcon) {
        setInterval(() => {
            boxIcon.classList.add('fa-box');
            boxIcon.classList.remove('fa-box-open');
            setTimeout(() => {
                boxIcon.classList.remove('fa-box');
                boxIcon.classList.add('fa-box-open');
            }, 1000);
        }, 2000);
    }

    // Yük maşını animasiyası
    const truckContainer = document.querySelector('.yoldadir-icon');
    if (truckContainer) {
        const truck = truckContainer.querySelector('.fa-truck');
        
        // Təkərlərin əlavə edilməsi
        const addWheels = () => {
            const wheelPositions = [
                { left: '25%', bottom: '-2px' },
                { left: '75%', bottom: '-2px' }
            ];
            
            wheelPositions.forEach(pos => {
                const wheel = document.createElement('div');
                wheel.className = 'truck-wheel';
                wheel.style.cssText = `
                    position: absolute;
                    width: 6px;
                    height: 6px;
                    background: #fff;
                    border-radius: 50%;
                    left: ${pos.left};
                    bottom: ${pos.bottom};
                    transform-origin: center;
                    animation: wheelRotate 1s linear infinite;
                `;
                truckContainer.appendChild(wheel);
            });
        };
        
        addWheels();

        // Yol və ağac effekti
        const roadContainer = document.createElement('div');
        roadContainer.className = 'road-container';
        roadContainer.style.cssText = `
            position: absolute;
            bottom: -15px;
            left: -20px;
            right: -20px;
            height: 2px;
            background: #fff;
            overflow: hidden;
        `;
        
        const road = document.createElement('div');
        road.className = 'road';
        road.style.cssText = `
            position: absolute;
            width: 200%;
            height: 100%;
            background: linear-gradient(90deg, #fff 50%, transparent 50%);
            background-size: 20px 100%;
            animation: roadMove 1s linear infinite;
        `;
        
        roadContainer.appendChild(road);
        truckContainer.appendChild(roadContainer);

        // Tüstü effekti
        const createSmoke = () => {
            const smoke = document.createElement('div');
            smoke.className = 'smoke';
            smoke.style.left = '10%';
            smoke.style.bottom = '30%';
            truckContainer.appendChild(smoke);
            
            setTimeout(() => smoke.remove(), 2000);
        };

        setInterval(createSmoke, 300);
    }

    // Çatdırıldı ikonu animasiyası
    const checkIcon = document.querySelector('.catdirildi-icon .fa-check-circle');
    if (checkIcon) {
        setInterval(() => {
            checkIcon.style.animation = 'tada 1s ease';
            setTimeout(() => {
                checkIcon.style.animation = '';
            }, 1000);
        }, 3000);
    }

    // CSS Animasiyaları
    const style = document.createElement('style');
    style.textContent = `
        @keyframes wheelRotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes roadMove {
            from { transform: translateX(0); }
            to { transform: translateX(-50%); }
        }
        
        .truck-container {
            position: relative;
            animation: truckBounce 1s ease-in-out infinite;
        }
        
        @keyframes truckBounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-2px); }
        }
    `;
    document.head.appendChild(style);

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

    window.addEventListener('scroll', () => {
        handleScrollAnimation();
    });

    handleScrollAnimation();

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

    // Browser-in geri düyməsini deaktiv et
    window.history.pushState(null, '', window.location.href);
    window.onpopstate = function() {
        window.history.pushState(null, '', window.location.href);
    };
});
