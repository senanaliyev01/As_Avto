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

// Məhsullar Səhifəsi
class ProductsPage {
    constructor() {
        // DOM elementlərini seçirik
        this.searchForm = utils.select('#searchForm');
        this.searchInput = utils.select('#searchInput');
        this.searchResults = utils.select('#searchResults');
        this.searchQuery = utils.select('#searchQuery');
        this.clearSearchBtn = utils.select('#clearSearch');
        this.productsGrid = utils.select('#productsGrid');
        this.productsCount = utils.select('#productsCount');
        this.noProducts = utils.select('#noProducts');
        
        // Filterlər
        this.categoryLinks = utils.selectAll('#categoryList .filter-link');
        this.brandLinks = utils.selectAll('#brandList .filter-link');
        this.markaLinks = utils.selectAll('#markaList .filter-link');
        
        // Aktiv filterlər
        this.activeFilters = {
            category: 'all',
            brand: 'all',
            marka: 'all'
        };
        
        // Axtarış mətni
        this.searchText = '';
        
        // Məhsulların sayı
        this.totalProducts = utils.selectAll('#productsGrid .grid-item').length;
        this.visibleProducts = this.totalProducts;
        
        this.init();
    }
    
    init() {
        if (!this.searchForm) return;
        
        // Olay dinləyicilərini qurur
        this.setupEventListeners();
        
        // Məhsulların sayını yeniləyirik
        this.updateProductCount();
    }
    
    setupEventListeners() {
        // Axtarış formu təqdim edildikdə
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSearch();
        });
        
        // Axtarış təmizlə düyməsi
        if (this.clearSearchBtn) {
            this.clearSearchBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }
        
        // Kateqoriya filter linkləri
        this.categoryLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.setActiveFilter(this.categoryLinks, link);
                this.activeFilters.category = link.getAttribute('data-category');
                this.filterProducts();
            });
        });
        
        // Brend filter linkləri
        this.brandLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.setActiveFilter(this.brandLinks, link);
                this.activeFilters.brand = link.getAttribute('data-brand');
                this.filterProducts();
            });
        });
        
        // Marka filter linkləri
        this.markaLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.setActiveFilter(this.markaLinks, link);
                this.activeFilters.marka = link.getAttribute('data-marka');
                this.filterProducts();
            });
        });
        
        // Axtarış inputu dəyişdikdə real vaxtda axtarış
        if (this.searchInput) {
            this.searchInput.addEventListener('input', utils.debounce(() => {
                if (this.searchInput.value.length >= 3 || this.searchInput.value.length === 0) {
                    this.handleSearch();
                }
            }, 300));
        }
    }
    
    handleSearch() {
        const query = this.searchInput.value.trim().toLowerCase();
        this.searchText = query;
        
        if (query) {
            // Axtarış nəticələri başlığını göstəririk
            this.searchResults.style.display = 'flex';
            this.searchQuery.textContent = query;
        } else {
            // Axtarış nəticələri başlığını gizlədirik
            this.searchResults.style.display = 'none';
        }
        
        this.filterProducts();
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.searchText = '';
        this.searchResults.style.display = 'none';
        this.filterProducts();
    }
    
    setActiveFilter(links, activeLink) {
        links.forEach(link => {
            link.classList.remove('active');
        });
        activeLink.classList.add('active');
    }
    
    filterProducts() {
        const items = utils.selectAll('#productsGrid .grid-item');
        let visibleCount = 0;
        
        items.forEach(item => {
            const category = item.getAttribute('data-category');
            const brand = item.getAttribute('data-brand');
            const marka = item.getAttribute('data-marka');
            const title = item.querySelector('.product-card__title').textContent.toLowerCase();
            const code = item.querySelector('.product-card__description:nth-of-type(3)').textContent.toLowerCase();
            
            // Kateqoriya, brend və markaya görə filter
            const categoryMatch = this.activeFilters.category === 'all' || category === this.activeFilters.category;
            const brandMatch = this.activeFilters.brand === 'all' || brand === this.activeFilters.brand;
            const markaMatch = this.activeFilters.marka === 'all' || marka === this.activeFilters.marka;
            
            // Axtarış mətninə görə filter
            const searchMatch = !this.searchText || 
                                title.includes(this.searchText) || 
                                code.includes(this.searchText);
            
            // Bütün filterlərə uyğundursa göstər
            if (categoryMatch && brandMatch && markaMatch && searchMatch) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        this.visibleProducts = visibleCount;
        this.updateProductCount();
        
        // Məhsul tapılmadı mesajını göstər və ya gizlət
        if (visibleCount === 0) {
            this.noProducts.style.display = 'flex';
            this.productsGrid.style.display = 'none';
        } else {
            this.noProducts.style.display = 'none';
            this.productsGrid.style.display = 'grid';
        }
    }
    
    updateProductCount() {
        if (this.productsCount) {
            this.productsCount.textContent = `${this.visibleProducts} məhsul`;
        }
    }
}

// Application initiation
document.addEventListener('DOMContentLoaded', () => {
    // Existing code
    new App();
    
    // Initialize Products Page
    const currentPath = window.location.pathname;
    if (currentPath.includes('mehsullar') || currentPath.includes('products')) {
        new ProductsPage();
    }
}); 