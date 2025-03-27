document.addEventListener('DOMContentLoaded', function() {
    // Filter elementlərini əldə edir
    const categoryFilter = document.getElementById('category-filter');
    const brandFilter = document.getElementById('brand-filter');
    const modelFilter = document.getElementById('model-filter');
    const stockFilter = document.getElementById('stock-filter');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');
    const noResultsElement = document.getElementById('no-results');
    const productContainer = document.getElementById('product-container');
    
    // Bütün məhsul kartlarını seçir
    const productCards = document.querySelectorAll('.product-card');
    
    // Məhsul sayğacı əlavə edir
    addProductCounter();
    
    // URL parametrlərinə görə filterləri yükləyir
    loadFiltersFromURL();
    
    // İlkin sayğac yüklənir
    updateProductCount();
    
    // Filter dəyişiklik hadisəsi
    const filters = [categoryFilter, brandFilter, modelFilter, stockFilter];
    
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            applyFilters();
            updateURLParameters();
        });
    });
    
    // Filterləri təmizləmə düyməsinə klik hadisəsi
    clearFiltersBtn.addEventListener('click', function() {
        clearFilters();
        updateURLParameters();
    });
    
    // Xəta mesajının filter sıfırlama düyməsi
    resetFiltersBtn.addEventListener('click', function() {
        clearFilters();
        updateURLParameters();
    });
    
    // Filterləri təmizləyir
    function clearFilters() {
        categoryFilter.value = '';
        brandFilter.value = '';
        modelFilter.value = '';
        stockFilter.value = '';
        
        applyFilters();
    }
    
    // Filterləri tətbiq edir
    function applyFilters() {
        // Filterlər tətbiq olunarkən yüklənmə animasiyası
        const initialOpacity = window.getComputedStyle(productContainer).opacity;
        productContainer.style.opacity = "0.6";
        productContainer.style.transition = "opacity 0.3s ease";
        
        const categoryValue = categoryFilter.value.toLowerCase();
        const brandValue = brandFilter.value.toLowerCase();
        const modelValue = modelFilter.value.toLowerCase();
        const stockValue = stockFilter.value.toLowerCase();
        
        let visibleCount = 0;
        
        productCards.forEach(card => {
            const category = card.getAttribute('data-category').toLowerCase();
            const brand = card.getAttribute('data-brand').toLowerCase();
            const model = card.getAttribute('data-model').toLowerCase();
            const stock = card.getAttribute('data-stock').toLowerCase();
            
            // Filter şərtləri yoxlanır
            const matchesCategory = !categoryValue || category === categoryValue;
            const matchesBrand = !brandValue || brand === brandValue;
            const matchesModel = !modelValue || model === modelValue;
            const matchesStock = !stockValue || stock === stockValue;
            
            // Kart göstərilir və ya gizlədilir
            if (matchesCategory && matchesBrand && matchesModel && matchesStock) {
                card.style.display = 'block';
                card.classList.add('fade-in');
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.classList.remove('fade-in');
            }
        });
        
        // Nəticə olmadığı halda mesajı göstərir
        if (visibleCount === 0) {
            noResultsElement.style.display = 'block';
            noResultsElement.classList.add('fade-in');
        } else {
            noResultsElement.style.display = 'none';
            noResultsElement.classList.remove('fade-in');
        }
        
        // Məhsul sayını yeniləyir
        updateProductCount(visibleCount);
        
        // Animasiyanı tamamlayır
        setTimeout(() => {
            productContainer.style.opacity = initialOpacity;
        }, 300);
    }
    
    // URL parametrlərini yeniləyir
    function updateURLParameters() {
        const params = new URLSearchParams();
        
        if (categoryFilter.value) params.set('category', categoryFilter.value);
        if (brandFilter.value) params.set('brand', brandFilter.value);
        if (modelFilter.value) params.set('model', modelFilter.value);
        if (stockFilter.value) params.set('stock', stockFilter.value);
        
        // URL-i parametrlərlə yeniləyir
        const newURL = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
        window.history.replaceState({}, '', newURL);
    }
    
    // URL parametrlərindən filterləri yükləyir
    function loadFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        if (params.has('category')) categoryFilter.value = params.get('category');
        if (params.has('brand')) brandFilter.value = params.get('brand');
        if (params.has('model')) modelFilter.value = params.get('model');
        if (params.has('stock')) stockFilter.value = params.get('stock');
        
        // Parametrlər varsa filterləri tətbiq edir
        if (params.toString()) {
            applyFilters();
        }
    }
    
    // Məhsul sayğacı əlavə edir
    function addProductCounter() {
        const counter = document.createElement('div');
        counter.className = 'product-counter';
        counter.id = 'product-counter';
        counter.innerHTML = `Göstərilən məhsullar: <span class="counter-value">0</span> / <span class="counter-total">0</span>`;
        
        // Sayğacı filter konteynerinə əlavə edir
        const filterHeader = document.querySelector('.filter-header');
        if (filterHeader) {
            filterHeader.appendChild(counter);
        }
    }
    
    // Məhsul sayını yeniləyir
    function updateProductCount(count) {
        const totalCount = productCards.length;
        const visibleCount = count !== undefined ? count : totalCount;
        
        const counterValue = document.querySelector('.counter-value');
        const counterTotal = document.querySelector('.counter-total');
        
        if (counterValue && counterTotal) {
            counterValue.textContent = visibleCount;
            counterTotal.textContent = totalCount;
        }
    }
}); 