document.addEventListener('DOMContentLoaded', function() {
    // Enhanced Scroll Animations
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight;
            
            if(elementPosition < screenPosition) {
                element.classList.add('animate');
            }
        });
    };

    // Enhanced Navbar Interaction
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;
    let isNavbarVisible = true;

    const handleNavbarVisibility = () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            navbar.style.transform = 'translateY(0)';
            navbar.style.backgroundColor = 'rgba(10, 25, 47, 0.95)';
            return;
        }
        
        if (currentScroll > lastScroll && isNavbarVisible) {
            navbar.style.transform = 'translateY(-100%)';
            isNavbarVisible = false;
        } else if (currentScroll < lastScroll && !isNavbarVisible) {
            navbar.style.transform = 'translateY(0)';
            navbar.style.backgroundColor = 'rgba(10, 25, 47, 0.98)';
            isNavbarVisible = true;
        }
        
        lastScroll = currentScroll;
    };

    // Parallax Effect for Hero Section
    const heroSection = document.querySelector('.hero-section');
    const parallaxEffect = () => {
        const scroll = window.pageYOffset;
        heroSection.style.backgroundPositionY = `${scroll * 0.5}px`;
    };

    // Enhanced Card Animations
    const cards = document.querySelectorAll('.delivery-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
        
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });

    // Enhanced Contact Information Interaction
    const contactElements = document.querySelectorAll('.manager-info a, .footer-contact a');
    contactElements.forEach(element => {
        element.addEventListener('click', function(e) {
            if (this.href.startsWith('tel:') || this.href.startsWith('mailto:')) {
                e.preventDefault();
                const text = this.href.includes('tel:') ? 
                    this.href.replace('tel:', '') : 
                    this.href.replace('mailto:', '');
                
                navigator.clipboard.writeText(text)
                    .then(() => showNotification('Məlumat kopyalandı!', 'success'))
                    .catch(() => showNotification('Kopyalama xətası!', 'error'));
            }
        });
    });

    // Enhanced Notification System
    const showNotification = (message, type = 'success') => {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        // Add animation
        notification.style.animation = 'slideIn 0.5s ease-out forwards';
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.5s ease-in forwards';
            setTimeout(() => {
                notification.className = 'notification';
            }, 500);
        }, 3000);
    };

    // Lazy Loading for Map
    const mapContainer = document.querySelector('.map-container');
    const lazyLoadMap = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const iframe = entry.target.querySelector('iframe');
                if (iframe && !iframe.src) {
                    iframe.src = iframe.dataset.src;
                    observer.unobserve(entry.target);
                }
            }
        });
    };

    const mapObserver = new IntersectionObserver(lazyLoadMap, {
        threshold: 0.1,
        rootMargin: '50px'
    });

    if (mapContainer) {
        mapObserver.observe(mapContainer);
    }

    // Event Listeners
    window.addEventListener('scroll', () => {
        handleNavbarVisibility();
        animateOnScroll();
        parallaxEffect();
    });

    // Initial calls
    animateOnScroll();
});