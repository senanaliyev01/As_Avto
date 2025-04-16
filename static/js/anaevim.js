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

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
    
    // Dropdown filter functionality
    const dropdownFilters = document.querySelectorAll('.dropdown-filter');
    
    dropdownFilters.forEach(filter => {
        const header = filter.querySelector('.dropdown-header');
        
        header.addEventListener('click', () => {
            // Close other open dropdowns
            dropdownFilters.forEach(df => {
                if (df !== filter && df.classList.contains('active')) {
                    df.classList.remove('active');
                }
            });
            
            // Toggle active class
            filter.classList.toggle('active');
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        dropdownFilters.forEach(filter => {
            if (!filter.contains(e.target) && filter.classList.contains('active')) {
                filter.classList.remove('active');
            }
        });
    });
    
    // Filter apply button
    const filterApplyBtn = document.querySelector('.filter-apply-btn');
    if (filterApplyBtn) {
        filterApplyBtn.addEventListener('click', () => {
            applyFilters();
        });
    }
    
    // Filter reset button
    const filterResetBtn = document.querySelector('.filter-reset-btn');
    if (filterResetBtn) {
        filterResetBtn.addEventListener('click', () => {
            resetFilters();
        });
    }
    
    // Mobile filter toggle functionality
    const filterToggle = document.querySelector('.filter-toggle');
    const filterSidebar = document.querySelector('.filter-sidebar');
    const filterOverlay = document.querySelector('.filter-overlay');
    
    if (filterToggle && filterSidebar && filterOverlay) {
        filterToggle.addEventListener('click', () => {
            filterSidebar.classList.add('active');
            filterOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
        
        filterOverlay.addEventListener('click', () => {
            filterSidebar.classList.remove('active');
            filterOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Search functionality
    setupSearch();
});

// Apply filters
function applyFilters() {
    // Get selected filters
    const selectedBrends = getSelectedValues('brend');
    const selectedMarkas = getSelectedValues('marka');
    
    // Build query string
    let queryParams = new URLSearchParams(window.location.search);
    
    // Add selected brands to query
    if (selectedBrends.length > 0) {
        queryParams.set('brand', selectedBrends.join(','));
    } else {
        queryParams.delete('brand');
    }
    
    // Add selected markas to query
    if (selectedMarkas.length > 0) {
        queryParams.set('model', selectedMarkas.join(','));
    } else {
        queryParams.delete('model');
    }
    
    // Redirect with new query params
    window.location.href = `${window.location.pathname}?${queryParams.toString()}`;
}

// Get selected values for a filter
function getSelectedValues(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    return Array.from(checkboxes).map(cb => cb.value);
}

// Reset all filters
function resetFilters() {
    // Uncheck all checkboxes
    document.querySelectorAll('.dropdown-item input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Redirect to base URL without query params
    window.location.href = window.location.pathname;
}

// Setup search functionality
function setupSearch() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const dropdownContainer = document.querySelector('.search-results-dropdown');
    
    if (!searchForm || !searchInput || !dropdownContainer) {
        return;
    }
    
    // Initially disable search button
    if (searchButton) {
        searchButton.disabled = !searchInput.value.trim();
    }
    
    let searchTimeout;
    
    // Input event with debounce
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim();
        
        // Update button state
        if (searchButton) {
            searchButton.disabled = !query;
        }
        
        // Clear previous timeout
        clearTimeout(searchTimeout);
        
        // If empty or short query, hide dropdown
        if (!query || query.length < 2) {
            dropdownContainer.classList.remove('active');
            return;
        }
        
        // Set new timeout for search
        searchTimeout = setTimeout(() => {
            performSearch(query, dropdownContainer);
        }, 300);
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchForm.contains(e.target)) {
            dropdownContainer.classList.remove('active');
        }
    });
    
    // Search form submit
    searchForm.addEventListener('submit', (e) => {
        const query = searchInput.value.trim();
        
        // Prevent empty submissions
        if (!query) {
            e.preventDefault();
            return false;
        }
        
        // Hide dropdown
        dropdownContainer.classList.remove('active');
        
        // Load results page
        window.location.href = `?search_text=${encodeURIComponent(query)}`;
        
        // Prevent form submission as we handle it manually
        e.preventDefault();
        return false;
    });
}

// Perform search API call
async function performSearch(query, dropdownContainer) {
    try {
        // Fetch search results
        const response = await fetch(`/realtime-search/?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            throw new Error('Axtarış sorğusu zamanı xəta baş verdi');
        }
        
        const data = await response.json();
        
        // Display results in dropdown
        if (data.results && data.results.length > 0) {
            const html = data.results.map(result => {
                const stockStatus = result.stok === 0 
                    ? '<div class="stock-status out-of-stock">Yoxdur</div>' 
                    : result.stok <= 20 
                        ? '<div class="stock-status low-stock">Az var</div>' 
                        : '<div class="stock-status in-stock">Var</div>';
                
                return `
                    <div class="search-result-item" onclick="window.location.href='/product/${encodeURIComponent(result.adi)}-${encodeURIComponent(result.oem)}-${encodeURIComponent(result.brend_kod)}/${result.id}/'">
                        ${result.sekil_url ? `<img src="${result.sekil_url}" alt="${result.adi}">` : ''}
                        <div class="search-result-info">
                            <h4>${result.adi}</h4>
                            <p>${result.brend} ${result.marka}</p>
                            <p>Kod: ${result.brend_kod} ${result.oem}</p>
                        </div>
                        <div class="search-result-price">
                            ${stockStatus}
                            ${result.qiymet} ₼
                        </div>
                    </div>
                `;
            }).join('');
            
            dropdownContainer.innerHTML = html;
            dropdownContainer.classList.add('active');
        } else {
            dropdownContainer.innerHTML = '<div class="search-result-item">Heç bir nəticə tapılmadı</div>';
            dropdownContainer.classList.add('active');
        }
    } catch (error) {
        console.error('Axtarış xətası:', error);
        dropdownContainer.innerHTML = '<div class="search-result-item">Xəta baş verdi</div>';
        dropdownContainer.classList.add('active');
    }
}

// Load existing filters from URL on page load
function loadFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);
    
    // Load brands
    if (params.has('brand')) {
        const brands = params.get('brand').split(',');
        brands.forEach(brand => {
            const checkbox = document.querySelector(`input[name="brend"][value="${brand}"]`);
            if (checkbox) checkbox.checked = true;
        });
    }
    
    // Load markas
    if (params.has('model')) {
        const markas = params.get('model').split(',');
        markas.forEach(marka => {
            const checkbox = document.querySelector(`input[name="marka"][value="${marka}"]`);
            if (checkbox) checkbox.checked = true;
        });
    }
}

// Call load filters when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    loadFiltersFromURL();
}); 