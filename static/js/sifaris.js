document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add smooth scroll behavior to order links
    const orderLinks = document.querySelectorAll('.sifaris-link');
    orderLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetElement = document.querySelector(href);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Add hover effects to statistics cards
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Animate progress steps on scroll
    const progressSteps = document.querySelectorAll('.progress-step');
    if (progressSteps.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.5
        });

        progressSteps.forEach(step => {
            step.style.opacity = '0';
            step.style.transform = 'translateY(20px)';
            step.style.transition = 'all 0.5s ease';
            observer.observe(step);
        });
    }

    // Add table row hover effects
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.backgroundColor = 'rgba(100, 255, 218, 0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.backgroundColor = '';
        });
    });

    // Animate numbers in statistics
    function animateValue(element, start, end, duration) {
        if (start === end) return;
        const range = end - start;
        let current = start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / range));
        
        const timer = setInterval(function() {
            current += increment;
            element.textContent = current.toFixed(2) + ' AZN';
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }

    // Animate statistics on page load
    const amountElements = document.querySelectorAll('.amount-info, .amount-info-1, .qaliq-borc');
    amountElements.forEach(element => {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = '0.00 AZN';
            animateValue(element, 0, value, 1000);
        }
    });

    // Add smooth transitions for status changes
    const statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(badge => {
        badge.style.transition = 'all 0.3s ease';
    });

    // Add loading animation for table
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer) {
        tableContainer.style.opacity = '0';
        tableContainer.style.transform = 'translateY(20px)';
        tableContainer.style.transition = 'all 0.5s ease';
        
        setTimeout(() => {
            tableContainer.style.opacity = '1';
            tableContainer.style.transform = 'translateY(0)';
        }, 300);
    }

    // Add ripple effect to clickable elements
    function createRipple(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
        ripple.style.width = ripple.style.height = '100px';
        ripple.style.transform = 'scale(0)';
        ripple.style.left = event.clientX - rect.left - 50 + 'px';
        ripple.style.top = event.clientY - rect.top - 50 + 'px';
        ripple.style.animation = 'ripple 0.6s linear';
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    const buttons = document.querySelectorAll('.stat-item, .sifaris-link');
    buttons.forEach(button => {
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.addEventListener('click', createRipple);
    });
});
