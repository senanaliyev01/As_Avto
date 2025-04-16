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
    
    // Scroll positionn
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
            this.header = new Header();
            this.heroSlider = new HeroSlider();
            this.mobileMenu = new MobileMenu();
            this.scrollAnimations = new ScrollAnimations();
            
            // Start components
            this.header.init();
            this.heroSlider.init();
            this.mobileMenu.init();
            this.scrollAnimations.init();
            
            // Initialize product sliders
            const sliderContainers = utils.selectAll('.slider-container');
            this.productSliders = sliderContainers.map(container => new ProductSlider(container));
            
            // Initialize brands slider
            const brandsSlider = utils.select('.brands-slider .slider-track');
            if (brandsSlider) {
                this.setupBrandsSlider(brandsSlider);
            }
            
            // Initialize product filters
            const productFiltersElement = utils.select('.product-filters');
            if (productFiltersElement) {
                this.productFilters = new ProductFilters();
                this.productFilters.init();
            }
            
            // Initialize price range slider
            const priceSlider = utils.select('.price-slider');
            if (priceSlider) {
                this.priceRangeSlider = new PriceRangeSlider();
                this.priceRangeSlider.init();
            }
        } catch (error) {
            console.error('Application initialization error:', error);
        }
    }
    
    setupBrandsSlider(slider) {
        // Clone items for infinite loop effect
        const items = utils.selectAll('.slider-item', slider);
        if (items.length === 0) return;
        
        // Clone items and append to slider
        items.forEach(item => {
            const clone = item.cloneNode(true);
            slider.appendChild(clone);
        });
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
        this.position = 0;
        this.speed = 0.3; // Daha yavaş sürət
        this.isPaused = false;
        this.lastTime = null;
        this.totalWidth = 0;
        
        this.init();
    }

    init() {
        this.setupInfiniteScroll();
        this.setupEventListeners();
        this.calculateTotalWidth();
        this.startAnimation();
    }

    setupInfiniteScroll() {
        const itemsToClone = Array.from(this.items);
        
        // Bütün elementləri 2 dəfə klonla
        for (let i = 0; i < 2; i++) {
            itemsToClone.forEach(item => {
                const clone = item.cloneNode(true);
                this.track.appendChild(clone);
            });
        }
    }

    calculateTotalWidth() {
        // Bütün elementlərin ümumi enini hesabla
        this.totalWidth = this.track.scrollWidth;
        
        // Elementlər arasındakı boşluğu hesabla
        const gap = parseInt(window.getComputedStyle(this.track).gap);
        this.totalWidth += (this.items.length * gap);
    }

    setupEventListeners() {
        // Mouse hover
        this.container.addEventListener('mouseenter', () => {
            this.isPaused = true;
        });

        this.container.addEventListener('mouseleave', () => {
            this.isPaused = false;
            this.lastTime = null;
        });
        
        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.isPaused = true;
            } else {
                this.isPaused = false;
                this.lastTime = null;
            }
        });

        // Pəncərə ölçüsü dəyişdikdə
        window.addEventListener('resize', () => {
            this.calculateTotalWidth();
        });
    }

    startAnimation() {
        const animate = (currentTime) => {
            if (this.lastTime === null) {
                this.lastTime = currentTime;
            }

            const deltaTime = currentTime - this.lastTime;

            if (!this.isPaused) {
                // Pozisiyanı yenilə
                this.position -= this.speed * deltaTime;

                // Bütün elementlər göründükdən sonra başa qaytar
                const itemWidth = this.items[0].offsetWidth;
                const gap = parseInt(window.getComputedStyle(this.track).gap);
                const resetPosition = -(itemWidth + gap) * this.items.length;

                if (Math.abs(this.position) >= Math.abs(resetPosition)) {
                    this.position = 0;
                }

                // Transform tətbiq et
                this.track.style.transform = `translateX(${this.position}px)`;
            }

            this.lastTime = currentTime;
            requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);
    }
}

// Product Filters Component
class ProductFilters {
    constructor() {
        this.filtersContainer = utils.select('.product-filters');
        this.filterToggle = utils.select('.filter-toggle');
        this.filterClose = utils.select('.filter-close');
        this.filterGroups = utils.selectAll('.filter-group--collapsible');
        this.applyFiltersBtn = utils.select('.apply-filters');
        this.isOpen = false;
    }

    init() {
        if (!this.filtersContainer) return;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Toggle mobile filters panel
        if (this.filterToggle) {
            this.filterToggle.addEventListener('click', () => this.toggleFilters());
        }
        
        // Close mobile filters panel
        if (this.filterClose) {
            this.filterClose.addEventListener('click', () => this.closeFilters());
        }
        
        // Collapsible filter groups
        this.filterGroups.forEach(group => {
            const title = group.querySelector('.filter-group__title');
            if (title) {
                title.addEventListener('click', () => this.toggleFilterGroup(group));
            }
        });
        
        // Apply filters
        if (this.applyFiltersBtn) {
            this.applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        }
        
        // Close filters when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !this.filtersContainer.contains(e.target) && 
                !this.filterToggle.contains(e.target)) {
                this.closeFilters();
            }
        });
        
        // Close filters on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeFilters();
            }
        });
        
        // Prevent body scroll when filters panel is open on mobile
        this.filtersContainer.addEventListener('touchmove', (e) => {
            if (this.isOpen && window.innerWidth <= 768) {
                // Allow scrolling inside the filters but not the body
                if (this.filtersContainer.scrollHeight > this.filtersContainer.clientHeight && 
                    this.isElementScrollable(this.filtersContainer)) {
                    e.stopPropagation();
                } else {
                    e.preventDefault();
                }
            }
        }, { passive: false });
    }
    
    isElementScrollable(element) {
        return element.scrollHeight > element.clientHeight;
    }

    toggleFilters() {
        this.isOpen ? this.closeFilters() : this.openFilters();
    }

    openFilters() {
        this.isOpen = true;
        this.filtersContainer.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeFilters() {
        this.isOpen = false;
        this.filtersContainer.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    toggleFilterGroup(group) {
        group.classList.toggle('filter-group--collapsed');
        const icon = group.querySelector('.filter-toggle-icon i');
        if (icon) {
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
        }
    }
    
    applyFilters() {
        // Collect all filter values
        const filters = {
            brands: [],
            makes: [],
            price: {
                min: parseFloat(utils.select('#min-value').value),
                max: parseFloat(utils.select('#max-value').value)
            }
        };
        
        // Collect brand filters
        utils.selectAll('input[name="brand"]:checked').forEach(input => {
            filters.brands.push(input.value);
        });
        
        // Collect make filters
        utils.selectAll('input[name="make"]:checked').forEach(input => {
            filters.makes.push(input.value);
        });
        
        console.log('Applied filters:', filters);
        
        // Close mobile filters after applying
        if (window.innerWidth <= 768) {
            this.closeFilters();
        }
        
        // Here you would normally filter the products or redirect with query params
        // For now we'll just log the filters
        
        // Animate the apply button to provide feedback
        this.animateApplyButton();
    }
    
    animateApplyButton() {
        if (!this.applyFiltersBtn) return;
        
        this.applyFiltersBtn.textContent = 'Filtrlər tətbiq edildi!';
        this.applyFiltersBtn.disabled = true;
        
        setTimeout(() => {
            this.applyFiltersBtn.textContent = 'Filtri tətbiq et';
            this.applyFiltersBtn.disabled = false;
        }, 2000);
    }
}

// Price Range Slider Component
class PriceRangeSlider {
    constructor() {
        this.rangeInputs = utils.selectAll('.range-input');
        this.priceInputs = utils.selectAll('.price-inputs input');
        this.range = utils.select('.slider-range');
        this.progress = utils.select('.slider-track');
        this.minVal = 0;
        this.maxVal = 1000;
        this.minGap = 100;
    }
    
    init() {
        if (this.rangeInputs.length < 2 || this.priceInputs.length < 2) return;
        
        this.setupEventListeners();
        this.updateView();
    }
    
    setupEventListeners() {
        // Update range slider when dragging
        this.rangeInputs.forEach(input => {
            input.addEventListener('input', () => this.updateRangeSlider(input));
        });
        
        // Update range slider when typing values
        this.priceInputs.forEach(input => {
            input.addEventListener('input', () => this.updateFromInput(input));
        });
    }
    
    updateRangeSlider(input) {
        this.minVal = parseInt(this.rangeInputs[0].value);
        this.maxVal = parseInt(this.rangeInputs[1].value);
        
        if (this.maxVal - this.minVal < this.minGap) {
            if (input === this.rangeInputs[0]) {
                this.minVal = this.maxVal - this.minGap;
                this.rangeInputs[0].value = this.minVal;
            } else {
                this.maxVal = this.minVal + this.minGap;
                this.rangeInputs[1].value = this.maxVal;
            }
        }
        
        // Update price inputs
        this.priceInputs[0].value = this.minVal;
        this.priceInputs[1].value = this.maxVal;
        
        this.updateView();
    }
    
    updateFromInput(input) {
        let minPrice = parseInt(this.priceInputs[0].value);
        let maxPrice = parseInt(this.priceInputs[1].value);
        
        if ((maxPrice - minPrice >= this.minGap) && maxPrice <= 1000) {
            if (input === this.priceInputs[0]) {
                this.minVal = minPrice;
                this.rangeInputs[0].value = minPrice;
            } else {
                this.maxVal = maxPrice;
                this.rangeInputs[1].value = maxPrice;
            }
        }
        
        this.updateView();
    }
    
    updateView() {
        // Calculate percentages for the range track
        const minPercent = (this.minVal / 1000) * 100;
        const maxPercent = (this.maxVal / 1000) * 100;
        
        // Update the range track and colored range
        if (this.range) {
            this.range.style.left = minPercent + '%';
            this.range.style.width = (maxPercent - minPercent) + '%';
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
}); 