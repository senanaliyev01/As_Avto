document.addEventListener('DOMContentLoaded', function() {
    // Status ikonlarına hover effekti
    const statusIcons = document.querySelectorAll('.status-badge i');
    statusIcons.forEach(icon => {
        icon.addEventListener('mouseenter', () => {
            icon.style.transform = 'scale(1.2)';
        });
        icon.addEventListener('mouseleave', () => {
            icon.style.transform = 'scale(1)';
        });
    });

    // Statistika kartlarına hover effekti
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateY(-10px)';
            item.style.boxShadow = '0 8px 16px rgba(100, 255, 218, 0.15)';
        });
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'translateY(0)';
            item.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });

    // Cədvəl sətirlərinə hover effekti
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transition = 'background-color 0.3s ease';
        });
    });

    // Progress bar animasiyası
    const progressSteps = document.querySelectorAll('.progress-step');
    if (progressSteps.length > 0) {
        progressSteps.forEach((step, index) => {
            setTimeout(() => {
                if (step.classList.contains('active')) {
                    step.style.opacity = '0';
                    step.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        step.style.transition = 'all 0.5s ease';
                        step.style.opacity = '1';
                        step.style.transform = 'scale(1)';
                    }, 100);
                }
            }, index * 200);
        });
    }

    // Qiymət formatlaması
    const formatPrice = (price) => {
        return parseFloat(price).toLocaleString('az-AZ', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    };

    // Qiymətləri formatla
    const priceElements = document.querySelectorAll('.amount-info, .amount-info-1, .qaliq-borc');
    priceElements.forEach(element => {
        const price = element.textContent.replace('AZN', '').trim();
        element.textContent = formatPrice(price) + ' AZN';
    });

    // Truck ikonuna tüstü effekti
    const addSmokeEffect = () => {
        const trucks = document.querySelectorAll('.truck-container');
        trucks.forEach(truck => {
            const smoke = truck.querySelector('.smoke');
            if (smoke) {
                setInterval(() => {
                    const newSmoke = document.createElement('div');
                    newSmoke.className = 'smoke-particle';
                    smoke.appendChild(newSmoke);
                    
                    setTimeout(() => {
                        newSmoke.remove();
                    }, 1000);
                }, 300);
            }
        });
    };

    addSmokeEffect();

    // Sifariş linklərinə hover effekti
    const orderLinks = document.querySelectorAll('.sifaris-link');
    orderLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            link.style.textDecoration = 'underline';
        });
        link.addEventListener('mouseleave', () => {
            link.style.textDecoration = 'none';
        });
    });

    // Mobil responsivlik üçün cədvəl scroll indikatorı
    const addTableScrollIndicator = () => {
        const tables = document.querySelectorAll('.table-container');
        tables.forEach(container => {
            if (container.scrollWidth > container.clientWidth) {
                const indicator = document.createElement('div');
                indicator.className = 'scroll-indicator';
                indicator.innerHTML = '<i class="fas fa-arrows-alt-h"></i>';
                container.parentNode.insertBefore(indicator, container);
                
                setTimeout(() => {
                    indicator.style.opacity = '0';
                }, 3000);
            }
        });
    };

    // Səhifə yükləndikdə və resize olduqda scroll indikatorunu yoxla
    addTableScrollIndicator();
    window.addEventListener('resize', addTableScrollIndicator);
});
