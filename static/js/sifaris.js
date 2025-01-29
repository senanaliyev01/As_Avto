document.addEventListener('DOMContentLoaded', function() {
    // Əsas dəyişənlər və konfiqurasiyalar
    const config = {
        animationDuration: 300,
        scrollThreshold: 90,
        hoverScaleAmount: 1.02
    };

    // Utility funksiyaları
    const utils = {
        debounce: (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        addClassName: (element, className) => {
            if (element && !element.classList.contains(className)) {
                element.classList.add(className);
            }
        },
        
        removeClassName: (element, className) => {
            if (element && element.classList.contains(className)) {
                element.classList.remove(className);
            }
        }
    };

    // Hover effektləri üçün təkmilləşdirilmiş funksiya
    const addHoverEffect = (elements, options = {}) => {
        const defaultOptions = {
            scale: config.hoverScaleAmount,
            duration: config.animationDuration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        elements.forEach(element => {
            element.style.transition = `transform ${finalOptions.duration}ms ${finalOptions.easing}`;
            
            element.addEventListener('mouseenter', () => {
                element.style.transform = `scale(${finalOptions.scale})`;
                element.style.zIndex = '1';
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.transform = 'scale(1)';
                element.style.zIndex = '0';
            });
        });
    };

    // Statistika kartları üçün təkmilləşdirilmiş animasiyalar
    const initializeStatCards = () => {
        const statItems = document.querySelectorAll('.stat-item');
        
        statItems.forEach((item, index) => {
            // Giriş animasiyası
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);

            // Hover effekti
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
                this.style.boxShadow = '0 20px 30px rgba(0,0,0,0.2)';
            });

            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = 'var(--shadow-lg)';
            });
        });
    };

    // Scroll animasiyası üçün təkmilləşdirilmiş funksiya
    const initializeScrollAnimations = () => {
        const scrollElements = document.querySelectorAll('.stat-item, .table-container, .info-row');
        
        const elementInView = (el, percentageScroll = config.scrollThreshold) => {
            const elementTop = el.getBoundingClientRect().top;
            const elementBottom = el.getBoundingClientRect().bottom;
            const windowHeight = window.innerHeight;
            
            return (
                elementTop <= windowHeight * (percentageScroll/100) &&
                elementBottom >= 0
            );
        };

        const displayScrollElement = element => {
            utils.addClassName(element, 'active');
            element.style.transform = 'translateY(0)';
            element.style.opacity = '1';
        };

        const hideScrollElement = element => {
            element.style.transform = 'translateY(20px)';
            element.style.opacity = '0';
        };

        scrollElements.forEach(el => {
            hideScrollElement(el);
        });

        const handleScrollAnimation = () => {
            scrollElements.forEach((el) => {
                if (elementInView(el, config.scrollThreshold)) {
                    displayScrollElement(el);
                }
            });
        };

        window.addEventListener('scroll', utils.debounce(handleScrollAnimation, 10));
        handleScrollAnimation();
    };

    // Cədvəl sıralama funksiyası
    const initializeTableSorting = () => {
        const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

        const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
            v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? 
            v1 - v2 : v1.toString().localeCompare(v2)
        )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

        document.querySelectorAll('th').forEach(th => {
            th.addEventListener('click', (() => {
                const table = th.closest('table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                // Vizual feedback
                th.style.transition = 'background-color 0.3s ease';
                th.style.backgroundColor = 'var(--accent-color)';
                setTimeout(() => {
                    th.style.backgroundColor = '';
                }, 300);

                // Sıralama
                rows.sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
                    .forEach(tr => tbody.appendChild(tr));
            }));
        });
    };

    // Tüstü effekti
    const createSmoke = (truckContainer) => {
        const smoke = document.createElement('div');
        smoke.className = 'smoke';
        truckContainer.appendChild(smoke);
        
        setTimeout(() => {
            smoke.remove();
        }, 2000);
    };

    // Progress addımları animasiyası
    const initializeProgressSteps = () => {
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

        // Tüstü effektini başlat
        document.querySelectorAll('.truck-container').forEach(container => {
            setInterval(() => {
                createSmoke(container);
            }, 300);
        });
    };

    // Browser geri düyməsini deaktiv et
    const disableBrowserBack = () => {
        window.history.pushState(null, '', window.location.href);
        window.onpopstate = function() {
            window.history.pushState(null, '', window.location.href);
        };
    };

    // Bütün funksiyaları işə sal
    const initialize = () => {
        initializeStatCards();
        initializeScrollAnimations();
        initializeTableSorting();
        initializeProgressSteps();
        disableBrowserBack();
        
        // Əlavə hover effektləri
        addHoverEffect(document.querySelectorAll('tbody tr'), { scale: 1.01 });
        addHoverEffect(document.querySelectorAll('.status-badge'), { scale: 1.05 });
    };

    // Səhifə yükləndikdə hər şeyi başlat
    initialize();
});
