// Utility functions
const utils = {
    // DOM element seçimi üçün qısa funksiya
    select: (selector, parent = document) => parent.querySelector(selector),
    selectAll: (selector, parent = document) => [...parent.querySelectorAll(selector)],
    
    // Element yaratmaq üçün helper
    createElement: (tag, className, text = '') => {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text) element.textContent = text;
        return element;
    },
    
    // Scroll position
    getScrollPosition: () => window.pageYOffset || document.documentElement.scrollTop,
    
    // Debounce function
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
    }
};

// Core Application Class
class App {
    constructor() {
        this.initializeComponents();
    }

    async initializeComponents() {
        try {
            // Initialize components
            this.preloader = new Preloader();
            this.header = new Header();
            this.heroSlider = new HeroSlider();
            this.mobileMenu = new MobileMenu();
            this.scrollAnimations = new ScrollAnimations();
            
            // Start components
            await this.preloader.init();
            this.header.init();
            this.heroSlider.init();
            this.mobileMenu.init();
            this.scrollAnimations.init();
            
            // Initialize product sliders
            const sliderContainers = utils.selectAll('.slider-container');
            this.productSliders = sliderContainers.map(container => new ProductSlider(container));
            
        } catch (error) {
            console.error('Application initialization error:', error);
        }
    }
}

// Preloader Component
class Preloader {
    constructor() {
        this.preloader = utils.select('.preloader');
    }

    async init() {
        if (!this.preloader) return;

        return new Promise(resolve => {
            if (document.readyState === 'complete') {
                this.hide(resolve);
            } else {
                window.addEventListener('load', () => this.hide(resolve));
            }
        });
    }

    hide(callback) {
        this.preloader.style.opacity = '0';
        setTimeout(() => {
            this.preloader.style.display = 'none';
            callback?.();
        }, 500);
    }
}

// Header Component
class Header {
    constructor() {
        this.header = utils.select('.header');
        this.lastScroll = 0;
        this.ticking = false;
    }

    init() {
        if (!this.header) return;
        
        window.addEventListener('scroll', () => {
            if (!this.ticking) {
                window.requestAnimationFrame(() => {
                    this.handleScroll();
                    this.ticking = false;
                });
                this.ticking = true;
            }
        });
    }

    handleScroll() {
        const currentScroll = utils.getScrollPosition();
        
        if (currentScroll <= 0) {
            this.header.classList.remove('header--hidden');
            return;
        }

        if (currentScroll > this.lastScroll && !this.header.classList.contains('header--hidden')) {
            // Scrolling down - hide header
            this.header.classList.add('header--hidden');
        } else if (currentScroll < this.lastScroll && this.header.classList.contains('header--hidden')) {
            // Scrolling up - show header
            this.header.classList.remove('header--hidden');
        }
        
        this.lastScroll = currentScroll;
    }
}

// Hero Slider Component
class HeroSlider {
    constructor() {
        this.container = utils.select('.hero__slider');
        this.slides = utils.selectAll('.hero__slide');
        this.prevBtn = utils.select('.hero__arrow--prev');
        this.nextBtn = utils.select('.hero__arrow--next');
        this.dotsContainer = utils.select('.hero__dots');
        
        this.currentIndex = 0;
        this.isPlaying = false;
        this.interval = 5000;
        this.slideInterval = null;
        
        // Touch events
        this.touchStartX = 0;
        this.touchEndX = 0;
    }

    init() {
        if (!this.container || this.slides.length === 0) return;
        
        this.createDots();
        this.setupEventListeners();
        this.start();
    }

    createDots() {
        this.slides.forEach((_, index) => {
            const dot = utils.createElement('button', 
                `hero__dot ${index === 0 ? 'hero__dot--active' : ''}`);
            dot.setAttribute('aria-label', `Slide ${index + 1}`);
            dot.addEventListener('click', () => this.goToSlide(index));
            this.dotsContainer.appendChild(dot);
        });
    }

    setupEventListeners() {
        // Arrow controls
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prev());
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.next());

        // Touch events with passive listeners for better performance
        this.container.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
            this.pause();
        }, { passive: true });

        this.container.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].clientX;
            this.handleSwipe();
            this.start();
        }, { passive: true });

        // Mouse events
        this.container.addEventListener('mouseenter', () => this.pause());
        this.container.addEventListener('mouseleave', () => this.start());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.prev();
            if (e.key === 'ArrowRight') this.next();
        });

        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pause();
            } else {
                this.start();
            }
        });
    }

    handleSwipe() {
        const diff = this.touchStartX - this.touchEndX;
        const threshold = 50;

        if (Math.abs(diff) > threshold) {
            if (diff > 0) this.next();
            else this.prev();
        }
    }

    goToSlide(index) {
        // Remove active class from current slide
        this.slides[this.currentIndex].classList.remove('active');
        
        // Update current index with boundary check
        this.currentIndex = (index + this.slides.length) % this.slides.length;

        // Activate new slide
        this.slides[this.currentIndex].classList.add('active');
        
        // Update dots
        this.updateDots();
    }

    updateDots() {
        utils.selectAll('.hero__dot', this.dotsContainer).forEach((dot, index) => {
            dot.classList.toggle('hero__dot--active', index === this.currentIndex);
        });
    }

    next() {
        this.goToSlide(this.currentIndex + 1);
    }

    prev() {
        this.goToSlide(this.currentIndex - 1);
    }

    start() {
        if (!this.isPlaying) {
            this.isPlaying = true;
            this.slideInterval = setInterval(() => this.next(), this.interval);
        }
    }

    pause() {
        if (this.isPlaying) {
            this.isPlaying = false;
            clearInterval(this.slideInterval);
        }
    }
}

// Mobile Menu Component
class MobileMenu {
    constructor() {
        this.toggle = utils.select('.header__toggle');
        this.nav = utils.select('.header__nav');
        this.menuLinks = utils.selectAll('.header__link');
        this.isOpen = false;
    }

    init() {
        if (!this.toggle || !this.nav) return;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Toggle menu
        this.toggle.addEventListener('click', () => this.toggleMenu());
        
        // Close menu when clicking links
        this.menuLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMenu());
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.nav.contains(e.target) && !this.toggle.contains(e.target)) {
                this.closeMenu();
            }
        });

        // Close menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });
    }

    toggleMenu() {
        this.isOpen ? this.closeMenu() : this.openMenu();
    }

    openMenu() {
        this.isOpen = true;
        this.toggle.classList.add('header__toggle--active');
        this.nav.classList.add('header__nav--active');
        document.body.style.overflow = 'hidden';
    }

    closeMenu() {
        this.isOpen = false;
        this.toggle.classList.remove('header__toggle--active');
        this.nav.classList.remove('header__nav--active');
        document.body.style.overflow = '';
    }
}

// Scroll Animations Component
class ScrollAnimations {
    constructor() {
        this.elements = utils.selectAll('.feature, .section__title, .about__content');
        this.observer = null;
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('fade-in');
                            this.observer.unobserve(entry.target);
                        }
                    });
                },
                {
                    threshold: 0.2,
                    rootMargin: '0px 0px -50px 0px'
                }
            );

            this.elements.forEach(element => this.observer.observe(element));
        } else {
            // Fallback for older browsers
            this.elements.forEach(element => element.classList.add('fade-in'));
        }
    }
}

// Product Slider Component
class ProductSlider {
    constructor(container) {
        this.container = container;
        this.track = container.querySelector('.slider-track');
        this.items = container.querySelectorAll('.slider-item');
        
        this.init();
    }

    init() {
        this.setupInfiniteScroll();
    }

    setupInfiniteScroll() {
        // Clone items for infinite scroll effect
        const itemsToClone = Array.from(this.items);
        itemsToClone.forEach(item => {
            const clone = item.cloneNode(true);
            this.track.appendChild(clone);
        });
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
}); 