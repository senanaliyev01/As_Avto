document.addEventListener('DOMContentLoaded', function() {
    // Utility funksiyaları
    const addClass = (el, className) => el.classList.add(className);
    const removeClass = (el, className) => el.classList.remove(className);
    const hasClass = (el, className) => el.classList.contains(className);

    // Animasiya effektləri
    const animateElement = (element, animation) => {
        element.style.animation = 'none';
        element.offsetHeight; // Force reflow
        element.style.animation = animation;
    };

    // Hover effektləri
    const addHoverEffect = (elements, options = {}) => {
        const defaults = {
            scale: 1.02,
            duration: 300,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        };
        const settings = { ...defaults, ...options };

        elements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.transition = `all ${settings.duration}ms ${settings.easing}`;
                element.style.transform = `scale(${settings.scale})`;
                element.style.zIndex = '1';
            });
            element.addEventListener('mouseleave', () => {
                element.style.transform = 'scale(1)';
                element.style.zIndex = '0';
            });
        });
    };

    // Cədvəl sətirləri üçün hover
    addHoverEffect(document.querySelectorAll('tbody tr'), { scale: 1.01 });

    // Status badge-ləri üçün hover
    addHoverEffect(document.querySelectorAll('.status-badge'), { scale: 1.05 });

    // Statistika kartları üçün hover və animasiya
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach((item, index) => {
        // Giriş animasiyası
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 200);

        // Hover effekti
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 15px 30px rgba(100, 255, 218, 0.15)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--shadow-lg)';
        });
    });

    // Scroll animasiyası
    const scrollElements = document.querySelectorAll('.stat-item, .table-container, .info-row');
    
    const elementInView = (el, offset = 0) => {
        const elementTop = el.getBoundingClientRect().top;
        const elementBottom = el.getBoundingClientRect().bottom;
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        
        return (
            elementTop <= windowHeight - offset &&
            elementBottom >= 0
        );
    };

    const displayScrollElement = element => {
        addClass(element, 'active');
        animateElement(element, 'fadeInUp 0.6s forwards');
    };

    const hideScrollElement = element => {
        removeClass(element, 'active');
    };

    const handleScrollAnimation = () => {
        scrollElements.forEach((el) => {
            if (elementInView(el, 100)) {
                displayScrollElement(el);
            } else {
                hideScrollElement(el);
            }
        });
    };

    // Debounce funksiyası
    const debounce = (fn, delay) => {
        let timeoutId;
        return (...args) => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            timeoutId = setTimeout(() => {
                fn.apply(null, args);
            }, delay);
        };
    };

    // Scroll event with debounce
    window.addEventListener('scroll', debounce(() => {
        handleScrollAnimation();
    }, 100));

    // İlk yükləmə
    handleScrollAnimation();

    // Status badge-ləri üçün pulsing effekt
    const badges = document.querySelectorAll('.status-badge');
    badges.forEach(badge => {
        const pulseAnimation = () => {
            animateElement(badge, 'pulse 2s infinite');
        };
        pulseAnimation();
    });

    // Cədvəl sıralama funksiyası
    const tableSort = (() => {
        const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;
        
        const comparer = (idx, asc) => (a, b) => {
            const v1 = getCellValue(asc ? a : b, idx);
            const v2 = getCellValue(asc ? b : a, idx);
            
            // Tarix formatı üçün xüsusi yoxlama
            if (v1.match(/^\d{2}\.\d{2}\.\d{4}$/)) {
                const [d1, m1, y1] = v1.split('.');
                const [d2, m2, y2] = v2.split('.');
                return new Date(y1, m1-1, d1) - new Date(y2, m2-1, d2);
            }
            
            // Rəqəm yoxlaması
            if (!isNaN(v1) && !isNaN(v2)) {
                return v1 - v2;
            }
            
            return v1.toString().localeCompare(v2);
        };

        document.querySelectorAll('th').forEach(th => {
            th.addEventListener('click', function() {
                const table = th.closest('table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const index = Array.from(th.parentNode.children).indexOf(th);
                
                // Sort direction göstəricisi
                const arrow = th.querySelector('.sort-arrow') || document.createElement('span');
                arrow.className = 'sort-arrow';
                
                // Əvvəlki oxları təmizlə
                th.parentNode.querySelectorAll('.sort-arrow').forEach(arr => {
                    if (arr !== arrow) arr.remove();
                });
                
                // Sort istiqamətini dəyiş
                const isAsc = !hasClass(arrow, 'asc');
                document.querySelectorAll('.sort-arrow').forEach(arr => {
                    removeClass(arr, 'asc');
                    removeClass(arr, 'desc');
                });
                
                addClass(arrow, isAsc ? 'asc' : 'desc');
                arrow.textContent = isAsc ? ' ↑' : ' ↓';
                
                if (!th.contains(arrow)) {
                    th.appendChild(arrow);
                }
                
                // Sıralama
                rows.sort(comparer(index, isAsc))
                    .forEach(tr => tbody.appendChild(tr));
            });
        });
    })();

    // Tüstü effekti
    const createSmoke = (truckContainer) => {
        const smoke = document.createElement('div');
        addClass(smoke, 'smoke');
        truckContainer.appendChild(smoke);
        
        setTimeout(() => {
            smoke.remove();
        }, 2000);
    };

    // Tüstü effektini başlat
    document.querySelectorAll('.truck-container').forEach(container => {
        setInterval(() => {
            createSmoke(container);
        }, 300);
    });

    // Progress addımlarını animasiya et
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        if (hasClass(step, 'active')) {
            setTimeout(() => {
                step.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    step.style.transform = 'scale(1)';
                }, 200);
            }, index * 300);
        }
    });

    // Browser-in geri düyməsini idarə et
    const handleBrowserNavigation = () => {
        window.history.pushState(null, '', window.location.href);
    };

    window.addEventListener('popstate', handleBrowserNavigation);
    handleBrowserNavigation();
});
